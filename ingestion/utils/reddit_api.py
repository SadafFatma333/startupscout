import os
import time
import random
import praw
from pathlib import Path
from prawcore.exceptions import RequestException, ResponseException, Forbidden, NotFound
from dotenv import load_dotenv
from utils.logger import setup_logger
from ingestion.utils.storage import load_existing_data, save_data

logger = setup_logger("startupscout.reddit_api")

# -----------------------------------------------------------
# Load credentials
# -----------------------------------------------------------
project_root = Path(__file__).resolve().parents[2]  # ingestion/utils → go up twice
ENV = os.getenv("ENV", "dev")
env_file = project_root / f".env.{ENV}"

if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv(project_root / ".env")

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT", "StartupScout/1.0")
USERNAME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")

if not all([CLIENT_ID, CLIENT_SECRET, USER_AGENT]):
    raise EnvironmentError("Missing Reddit credentials in .env file")

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
    username=USERNAME,
    password=PASSWORD,
    check_for_async=False,
    requestor_kwargs={"timeout": 30},
)

# -----------------------------------------------------------
# Constants
# -----------------------------------------------------------
MAX_RETRIES = 5
MAX_GLOBAL_FAILURES = 10
GLOBAL_SLEEP_MIN = 15 * 60  # 15 minutes cooldown
POST_SLEEP = (0.8, 1.5)
COMMENT_SLEEP = (1.0, 2.0)
LONG_SLEEP_LIMIT = 900  # cap individual backoff at 15 minutes

# -----------------------------------------------------------
# Helper: Safe API sleep with logs
# -----------------------------------------------------------
def safe_sleep(seconds, reason=""):
    minutes = round(seconds / 60, 2)
    if minutes >= 1:
        logger.warning(f"Sleeping {minutes} min. Reason: {reason}")
    else:
        logger.debug(f"Sleeping {seconds:.1f}s. Reason: {reason}")
    time.sleep(seconds)

# -----------------------------------------------------------
# Fetch subreddit posts
# -----------------------------------------------------------
def fetch_subreddit_page(subreddit: str, limit: int = 100):
    posts_data = []
    logger.info(f"Fetching subreddit '{subreddit}' via Reddit API (limit={limit})")

    start_time = time.time()
    try:
        for i, submission in enumerate(reddit.subreddit(subreddit).new(limit=limit), 1):
            posts_data.append(
                {
                    "id": submission.id,
                    "title": submission.title,
                    "selftext": submission.selftext or "",
                    "url": f"https://www.reddit.com{submission.permalink}",
                    "created_utc": submission.created_utc,
                    "subreddit": subreddit,
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                }
            )
            if i % 25 == 0:
                elapsed = round(time.time() - start_time, 1)
                logger.info(f"Fetched {i}/{limit} posts from r/{subreddit} (elapsed {elapsed}s)")
            time.sleep(random.uniform(*POST_SLEEP))
    except Exception as e:
        logger.error(f"Error fetching subreddit '{subreddit}': {e}")

    logger.info(f"Fetched {len(posts_data)} posts from r/{subreddit}")
    return posts_data

# -----------------------------------------------------------
# Robust comment fetch with rate-limit control
# -----------------------------------------------------------
def fetch_comments_safe(submission_id: str):
    for attempt in range(MAX_RETRIES):
        try:
            submission = reddit.submission(id=submission_id)
            submission.comments.replace_more(limit=0)
            return [c.body for c in submission.comments.list()]

        except (RequestException, ResponseException, Forbidden, NotFound) as e:
            msg = str(e)
            if "429" in msg or "RATELIMIT" in msg.upper() or "timed out" in msg.lower():
                wait = min(LONG_SLEEP_LIMIT, (2 ** attempt) * 60 + random.randint(10, 60))
                safe_sleep(wait, f"Rate limit or timeout on {submission_id}")
                continue
            logger.warning(f"Transient error on {submission_id}: {e}")
            safe_sleep(60, "transient Reddit API issue")
            continue

        except Exception as e:
            logger.error(f"Unrecoverable error fetching {submission_id}: {e}")
            return []

    logger.error(f"Max retries reached for {submission_id}, skipping.")
    return []

# -----------------------------------------------------------
# Enrich with comments (resumable)
# -----------------------------------------------------------
def enrich_with_comments(subreddit: str, output_path: str, limit: int = 100):
    """Fetch new posts and enrich them with comments, safe and resumable."""
    logger.info(f"=== Starting ingestion for r/{subreddit} ===")

    data_path = Path(output_path)
    data = load_existing_data(data_path)
    existing_ids = {p["id"] for p in data.values()} if isinstance(data, dict) else set()
    logger.info(f"Loaded {len(existing_ids)} existing posts from {output_path}")

    new_posts = fetch_subreddit_page(subreddit, limit=limit)
    logger.info(f"Processing {len(new_posts)} posts for enrichment...")

    enriched = 0
    consecutive_failures = 0

    for post in new_posts:
        if post["id"] in existing_ids:
            continue
        try:
            post["comments"] = fetch_comments_safe(post["id"])
            if isinstance(data, dict):
                data[post["url"]] = post
            else:
                data.append(post)
            enriched += 1
            save_data(data, data_path)
            logger.info(f"Saved post {post['id']} ({enriched} new so far).")
            safe_sleep(random.uniform(*COMMENT_SLEEP), "between comment fetches")

        except Exception as e:
            consecutive_failures += 1
            logger.warning(f"Error processing {post['id']}: {e}")
            if consecutive_failures >= MAX_GLOBAL_FAILURES:
                safe_sleep(GLOBAL_SLEEP_MIN, "too many consecutive failures")
                consecutive_failures = 0
            continue

    logger.info(
        f"Completed ingestion for r/{subreddit}: total {len(data)} posts ({enriched} new added)."
    )
    save_data(data, data_path)
    logger.info(f"Final save complete → {output_path}")
    return data

# -----------------------------------------------------------
# CLI entrypoint
# -----------------------------------------------------------
if __name__ == "__main__":
    OUTPUT_PATH = str(project_root / "data/raw/reddit_posts.json")
    SUBREDDITS = ["startups", "Entrepreneur"]

    for sub in SUBREDDITS:
        enrich_with_comments(sub, OUTPUT_PATH, limit=500)
        safe_sleep(600, f"Cooldown before next subreddit ({sub})")

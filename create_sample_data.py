#!/usr/bin/env python3
"""
Generate sample startup data for testing StartupScout
"""

import json
import os
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Generate realistic sample startup data."""
    
    sample_cases = [
        {
            "title": "How to Raise Series A Funding",
            "decision": "We decided to raise Series A funding after achieving $100K MRR and 40% month-over-month growth. We prepared a comprehensive pitch deck highlighting our traction, market opportunity, and team.",
            "summary": "Successfully raised $5M Series A from top-tier VCs after demonstrating strong product-market fit and scalable growth metrics.",
            "content": "Our startup had been bootstrapped for 18 months and reached $100K monthly recurring revenue. We had 40% month-over-month growth and strong customer retention. The decision to raise Series A came after analyzing our runway and growth potential. We prepared a detailed pitch deck covering our problem, solution, market size, traction, business model, team, and financial projections. We targeted VCs who had experience with B2B SaaS companies in our space. The fundraising process took 4 months and we closed $5M at a $20M pre-money valuation.",
            "source": "YC Library",
            "stage": "Series A",
            "tags": ["funding", "series-a", "pitch-deck", "vc", "growth"],
            "created_at": (datetime.now() - timedelta(days=30)).isoformat()
        },
        {
            "title": "Choosing Between B2B and B2C Markets",
            "decision": "After extensive market research, we pivoted from B2C to B2B after realizing enterprise customers had higher willingness to pay and longer retention rates.",
            "summary": "Pivoted to B2B model resulting in 3x higher ARPU and 60% lower churn rate compared to B2C approach.",
            "content": "Initially, we built a consumer-focused productivity app but struggled with monetization and high churn rates. After 6 months of user interviews and market analysis, we discovered that enterprise customers were willing to pay $50-200 per user per month for similar functionality. We redesigned our product for B2B use cases, added admin controls, SSO integration, and compliance features. The pivot took 3 months and resulted in our first enterprise customer paying $5K/month for 100 users. This validated our B2B strategy and we focused all efforts on enterprise sales.",
            "source": "Indie Hackers",
            "stage": "Early Stage",
            "tags": ["pivot", "b2b", "enterprise", "monetization", "strategy"],
            "created_at": (datetime.now() - timedelta(days=45)).isoformat()
        },
        {
            "title": "Building a Remote-First Team",
            "decision": "We decided to go fully remote after our first hire, focusing on async communication and building a strong company culture through regular virtual events.",
            "summary": "Remote-first approach enabled us to hire top talent globally and reduce operational costs by 40% while maintaining high productivity.",
            "content": "As a distributed team from day one, we invested heavily in remote-first processes. We use Slack for async communication, Notion for documentation, and weekly all-hands meetings. We implemented 'no meeting Wednesdays' for deep work and quarterly in-person retreats for team bonding. Our hiring process includes async work samples and culture fit interviews. This approach allowed us to hire senior engineers from Silicon Valley while being based in a lower-cost location. Our team productivity metrics show 95% of our team feels more productive working remotely.",
            "source": "Reddit r/startups",
            "stage": "Growth",
            "tags": ["remote-work", "team-building", "culture", "hiring", "productivity"],
            "created_at": (datetime.now() - timedelta(days=20)).isoformat()
        },
        {
            "title": "Pricing Strategy for SaaS Product",
            "decision": "We implemented a freemium model with usage-based pricing tiers after analyzing competitor pricing and conducting customer interviews.",
            "summary": "Freemium model increased signups by 300% and conversion rate by 25%, with average customer LTV increasing to $2,400.",
            "content": "After testing different pricing models, we settled on a freemium approach with three tiers: Free (up to 1,000 API calls), Pro ($29/month for 10K calls), and Enterprise ($99/month for unlimited). We used customer interviews to validate pricing sensitivity and competitor analysis to position ourselves in the market. The freemium tier serves as our primary acquisition channel, with 15% converting to paid plans. Our pricing page includes a calculator showing ROI and we offer annual discounts. This strategy helped us reach $50K ARR within 8 months of launch.",
            "source": "Medium",
            "stage": "Early Stage",
            "tags": ["pricing", "saas", "freemium", "conversion", "strategy"],
            "created_at": (datetime.now() - timedelta(days=35)).isoformat()
        },
        {
            "title": "Technical Architecture Decisions",
            "decision": "We chose microservices architecture over monolithic design to enable independent scaling and faster development cycles.",
            "summary": "Microservices architecture reduced deployment time by 70% and enabled team autonomy, though it increased initial complexity.",
            "content": "After evaluating monolithic vs microservices architectures, we chose microservices for our B2B platform. We use Docker containers, Kubernetes for orchestration, and API Gateway for routing. Each service owns its data and communicates via REST APIs. This allows different teams to work independently and deploy services separately. While it increased initial setup complexity, it paid off when we needed to scale our payment processing service independently. We use service mesh for monitoring and tracing. The architecture supports our goal of 99.9% uptime and enables rapid feature development.",
            "source": "Engineering Blog",
            "stage": "Growth",
            "tags": ["architecture", "microservices", "scaling", "devops", "engineering"],
            "created_at": (datetime.now() - timedelta(days=25)).isoformat()
        },
        {
            "title": "Customer Acquisition Strategy",
            "decision": "We focused on content marketing and SEO as our primary acquisition channels after paid ads showed poor unit economics.",
            "summary": "Content marketing strategy generated 60% of new customers at 80% lower CAC compared to paid advertising channels.",
            "content": "Initially, we spent $10K/month on Google Ads and Facebook ads but struggled with high customer acquisition costs ($150 CAC vs $50 LTV). We pivoted to content marketing, publishing 2-3 blog posts per week about industry trends and best practices. We optimized for long-tail keywords and created comprehensive guides. This strategy took 3 months to show results but eventually generated 60% of our new customers organically. Our content team includes a technical writer and SEO specialist. We also launched a podcast interviewing industry experts, which drives 20% of our traffic.",
            "source": "Marketing Case Study",
            "stage": "Growth",
            "tags": ["marketing", "content", "seo", "acquisition", "cac"],
            "created_at": (datetime.now() - timedelta(days=40)).isoformat()
        },
        {
            "title": "Hiring First Technical Co-founder",
            "decision": "We brought on a technical co-founder with 10 years of experience after realizing our technical debt was limiting growth.",
            "summary": "Technical co-founder helped reduce bugs by 80% and increased development velocity by 3x, enabling faster feature delivery.",
            "content": "As non-technical founders, we initially outsourced development but accumulated significant technical debt. After 18 months, we realized we needed a technical co-founder to scale properly. We offered 25% equity to attract a senior engineer with startup experience. The co-founder restructured our codebase, implemented proper testing, and established development processes. Within 6 months, we reduced production bugs by 80% and increased feature delivery speed by 3x. The co-founder also helped us make better technical decisions and hire additional engineers.",
            "source": "Founder Story",
            "stage": "Early Stage",
            "tags": ["hiring", "co-founder", "technical", "equity", "team"],
            "created_at": (datetime.now() - timedelta(days=50)).isoformat()
        },
        {
            "title": "International Expansion Strategy",
            "decision": "We expanded to European markets first due to GDPR compliance requirements and higher willingness to pay for privacy-focused solutions.",
            "summary": "European expansion contributed 35% of new revenue within 6 months, with 40% higher ARPU compared to US customers.",
            "content": "After achieving product-market fit in the US, we evaluated international expansion options. Europe was attractive due to GDPR compliance requirements creating barriers for competitors and higher willingness to pay for privacy-focused solutions. We hired a European sales manager and localized our product for German, French, and UK markets. We also established a European entity for tax optimization. The expansion required 6 months of preparation including legal setup, localization, and compliance. European customers showed 40% higher ARPU and lower churn rates.",
            "source": "Expansion Case Study",
            "stage": "Scale",
            "tags": ["international", "expansion", "gdpr", "localization", "revenue"],
            "created_at": (datetime.now() - timedelta(days=15)).isoformat()
        }
    ]
    
    return sample_cases

def create_data_directory():
    """Create data directory and save sample data."""
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    sample_data = generate_sample_data()
    
    # Save to startup_data.json
    data_file = os.path.join(data_dir, "startup_data.json")
    with open(data_file, "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"✅ Created {len(sample_data)} sample startup cases")
    print(f"📁 Saved to: {data_file}")
    
    return data_file

if __name__ == "__main__":
    create_data_directory()

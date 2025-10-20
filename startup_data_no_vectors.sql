--
-- PostgreSQL database dump
--

\restrict RFVgtKHUgKvTtLNuPqMoGPPMYND30Fn7QZ9BfCspr5KuJKZquuMfGZrXGj7gpH7

-- Dumped from database version 15.4 (Debian 15.4-2.pgdg120+1)
-- Dumped by pg_dump version 15.14 (Debian 15.14-1.pgdg12+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: decisions; Type: TABLE DATA; Schema: public; Owner: postgres
--

\.


--
-- Data for Name: rag_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rag_items (event_id, rank, url, title, source, sim, ce, kw, rrf) FROM stdin;
1	1	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1n33yiq/how_do_you_figure_out_pricing_strategy_for_your/	how do you figure out pricing strategy for your saas product?	reddit	0.643281796174158	\N	\N	\N
1	2	https://www.reddit.com/r/startups/comments/1o11m2n/pricing_my_first_product_felt_harder_than/	pricing my first product felt harder than building it - i will not promote	reddit	0.607914603228248	\N	\N	\N
1	3	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1nlbsq4/how_i_picked_a_startup_idea_worth_millions_and/	how i picked a startup idea worth millions (and closed billion-dollar brands)	reddit	0.51942235462932	\N	\N	\N
1	4	https://medium.com/@mikesparr/my-saas-go-to-market-playbook-6f2b4603a777?source=rss------tech_startups-5	my saas go to market playbook	medium	0.513634891130621	\N	\N	\N
1	5	https://www.reddit.com/r/Startup_Ideas/comments/1nxa71y/were_senior_devs_who_normally_work_with_corporate/	we're senior devs who normally work with corporate but now looking to work with startups on smaller projects	reddit	0.524809796334773	\N	\N	\N
2	1	https://www.reddit.com/r/startups/comments/1nysgtj/stop_chasing_millions_focus_on_your_first_10/	stop chasing millions. focus on your first 10 users. (i will not promote)	reddit	0.455317505243271	\N	\N	\N
2	2	https://www.reddit.com/r/Entrepreneur/comments/1nykya0/what_i_learned_after_50_founders_argued_about/	what i learned after 50 founders argued about ideas vs execution	reddit	0.452620755370337	\N	\N	\N
2	3	https://www.reddit.com/r/SaaS/comments/1o2wq7c/aipowered_saas_founders_how_do_you_manage_your/	ai-powered saas founders. how do you manage your prompts?	reddit	0.45860178645259	\N	\N	\N
2	4	https://www.reddit.com/r/SaaS/comments/1o395n5/the_feature_that_killed_my_momentum/	the feature that killed my momentum	reddit	0.466102274292573	\N	\N	\N
2	5	https://www.reddit.com/r/startups/comments/1nhsre4/i_will_not_promote_the_dream_tool_for_product/	[i will not promote] the dream tool for product focused solo-founders?	reddit	0.471107335620682	\N	\N	\N
3	1	https://www.reddit.com/r/startups/comments/1nuhe1e/i_will_not_promote_how_to_actually_close_deals/	[i will not promote] how to actually close deals from cold outreach leads	reddit	0.457524662312909	\N	\N	\N
4	1	https://www.reddit.com/r/startups/comments/1noktjj/do_you_define_your_icp_early_or_sell_to_everyone/	do you define your icp early or sell to everyone first? sharing what worked for me (20k+ users) and curious what worked for you. i will not promote	reddit	0.583454251289384	\N	\N	\N
5	1	https://www.reddit.com/r/startups/comments/1o0pncy/how_to_get_first_early_100_users_i_will_not/	how to get first early 100 users "i will not promote"	reddit	0.580510472089677	\N	\N	\N
5	2	https://www.reddit.com/r/SaaS/comments/1o3ito1/does_everyone_secretly_use_scrapers_cold_email/	does everyone secretly use scrapers, cold email, and automated outreach to get their first 100-200 saas customers?	reddit	0.582127546198819	\N	\N	\N
5	3	https://www.reddit.com/r/SaaS/comments/1o378d7/whats_your_1_tip_for_getting_your_first_saas/	what's your #1 tip for getting your first saas customers and marketing on a limited budget?	reddit	0.546750995323122	\N	\N	\N
5	4	https://www.reddit.com/r/SaaS/comments/1o3fgby/1_my_linkedin_post_was_liked_by_julie_zhuo_one_of/	#1 my linkedin post was liked by julie zhuo - one of my favorite product managers!!!\n#2 got 11 solid new users this week after finding the right timing to ask for emails.\n#3 after implementing the strategy to capture anonymous visitors, i had 13 visitors in the past 24 hours.	reddit	0.544942384355352	\N	\N	\N
5	5	https://www.reddit.com/r/startups/comments/1nysgtj/stop_chasing_millions_focus_on_your_first_10/	stop chasing millions. focus on your first 10 users. (i will not promote)	reddit	0.54918273990258	\N	\N	\N
6	1	https://www.reddit.com/r/SaaS/comments/1o1lz29/the_5_best_first_check_startup_investors/	the 5 best first check startup investors	reddit	0.618447620226372	\N	\N	\N
6	2	https://medium.com/@valenpodda/how-to-nail-fundraising-in-pre-seed-and-seed-stage-a-founders-playbook-77ad7b5e7317?source=rss------fundraising-5	how to nail fundraising in pre-seed and seed stage: a founder’s playbook.	medium	0.532552389350392	\N	\N	\N
6	3	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1npqzl2/stay_away_from_vcs_or_no/	stay away from vcs or no?	reddit	0.546745538711548	\N	\N	\N
6	4	https://www.reddit.com/r/Entrepreneur/comments/1nxdgck/first_time_founder_end_of_2nd_officially_raising/	first time founder, end of 2nd officially raising	reddit	0.520751237869263	\N	\N	\N
6	5	https://www.reddit.com/r/startups/comments/1nn31na/curious_what_angels_prioritize_most_when_backing/	curious what angels prioritize most when backing pre-seed companies? (i will not promote)	reddit	0.554621862263251	\N	\N	\N
7	1	https://www.reddit.com/r/indiehackers/comments/1o33yfk/letting_users_try_before_signup_boosted/	letting users try before signup boosted engagement — small update on logosmith	reddit	0.592190875019276	\N	\N	\N
7	2	https://www.reddit.com/r/SaaS/comments/1o2yrby/stuck_under_500_mrr_a_practical_nofluff_playbook/	stuck under $500 mrr? a practical, no-fluff playbook to break the plateau	reddit	0.548715227995492	\N	\N	\N
7	3	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1nf1a4r/customer_onboarding_optimization_that_cut_churn/	customer onboarding optimization that cut churn 47%: 7-day sequence + activation metrics that actually predict retention	reddit	0.604598439013892	\N	\N	\N
7	4	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1nl6vpl/adding_friction_into_onboarding_flow_to_reach/	adding friction into onboarding flow to reach activation event faster	reddit	0.529071324093026	\N	\N	\N
7	5	https://www.reddit.com/r/SaaS/comments/1o2yww1/how_i_got_my_first_10_customers_in_30_days_no_ads/	how i got my first 10 customers in 30 days - no ads, no influencers, just scrappy experiments	reddit	0.551626008167506	\N	\N	\N
8	1	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1n33yiq/how_do_you_figure_out_pricing_strategy_for_your/	how do you figure out pricing strategy for your saas product?	reddit	0.643281796174158	\N	\N	\N
8	2	https://www.reddit.com/r/startups/comments/1o11m2n/pricing_my_first_product_felt_harder_than/	pricing my first product felt harder than building it - i will not promote	reddit	0.607914603228248	\N	\N	\N
8	3	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1nlbsq4/how_i_picked_a_startup_idea_worth_millions_and/	how i picked a startup idea worth millions (and closed billion-dollar brands)	reddit	0.51942235462932	\N	\N	\N
8	4	https://medium.com/@mikesparr/my-saas-go-to-market-playbook-6f2b4603a777?source=rss------tech_startups-5	my saas go to market playbook	medium	0.513634891130621	\N	\N	\N
8	5	https://www.reddit.com/r/Startup_Ideas/comments/1nxa71y/were_senior_devs_who_normally_work_with_corporate/	we're senior devs who normally work with corporate but now looking to work with startups on smaller projects	reddit	0.524809796334773	\N	\N	\N
9	1	https://medium.com/@mikesparr/my-saas-go-to-market-playbook-6f2b4603a777?source=rss------tech_startups-5	my saas go to market playbook	medium	0.550677320240032	\N	\N	\N
9	2	https://www.reddit.com/r/SaaS/comments/1o34fmr/why_92_of_saas_startups_fail_in_2025/	why 92% of saas startups fail in 2025	reddit	0.643871311449184	\N	\N	\N
9	3	https://www.reddit.com/r/SaaS/comments/1o22fjn/0_to_100k_arr_in_90_days_sounds_great_until_you/	“$0 to $100k arr in 90 days” - sounds great, until you read the fine print	reddit	0.530530652245686	\N	\N	\N
9	4	https://www.reddit.com/r/startups/comments/1nrpw87/paywhatyouwant_building_a_tribe_not_just_a/	pay-what-you-want: building a tribe, not just a userbase [i will not promote]	reddit	0.551812788519966	\N	\N	\N
9	5	https://www.reddit.com/r/SaaS/comments/1o27z70/forget_unicorns_10k_mrr_solo_feels_better_than_2m/	forget unicorns. $10k mrr solo feels better than $2m seed and stress	reddit	0.543266556870966	\N	\N	\N
10	1	https://www.reddit.com/r/indiehackers/comments/1nyrcrb/built_validating_it_to_test_startup_ideas_faster/	built validating it to test startup ideas faster — here’s what i learned in 2 weeks	reddit	0.708781961391744	\N	\N	\N
10	2	https://medium.com/@desifounder/startups-101-how-to-validate-a-startup-idea-f87a9f14a6d0?source=rss------startups_101-5	startups 101: how to validate a startup idea	medium	0.676813522672253	\N	\N	\N
10	3	https://www.reddit.com/r/Startup_Ideas/comments/1o2glt4/i_made_a_list_of_ready_to_use_validated_startup/	i made a list of ready to use validated startup ideas	reddit	0.708598140650822	\N	\N	\N
10	4	https://www.reddit.com/r/SideProject/comments/1o3tfb7/how_to_validate_a_side_project_idea_without/	how to validate a side project idea without spending a buck	reddit	0.644596017091875	\N	\N	\N
10	5	https://www.reddit.com/r/Startup_Ideas/comments/1nkpe5f/should_i_build_this_game_for_indie_founders/	should i build this game for indie founders?	reddit	0.657855887945172	\N	\N	\N
11	1	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1n33yiq/how_do_you_figure_out_pricing_strategy_for_your/	how do you figure out pricing strategy for your saas product?	reddit	0.661051710781354	\N	\N	\N
11	2	https://www.reddit.com/r/SaaS/comments/1o2my3m/building_in_public_financial_data_api_launching/	building in public: financial data api (launching january 2026) - lessons learned analyzing competitors	reddit	0.589542914683471	\N	\N	\N
11	3	https://www.reddit.com/r/startups/comments/1o11m2n/pricing_my_first_product_felt_harder_than/	pricing my first product felt harder than building it - i will not promote	reddit	0.607232892082162	\N	\N	\N
11	4	https://www.reddit.com/r/SaaS/comments/1o1u29b/ill_build_your_b2b_sales_funnel_thatll_be/	i’ll build your b2b sales funnel that’ll be profitable in 30 days	reddit	0.553863730796354	\N	\N	\N
11	5	https://www.reddit.com/r/SaaS/comments/1o34fmr/why_92_of_saas_startups_fail_in_2025/	why 92% of saas startups fail in 2025	reddit	0.541255680247804	\N	\N	\N
12	1	https://www.reddit.com/r/startups/comments/1nfhsxx/fundraising_terms_for_a_company_thats_mostly/	fundraising terms for a company that’s mostly bootstrapping (i will not promote)	reddit	0.624376952648203	\N	\N	\N
12	2	https://www.reddit.com/r/startups/comments/1o0cata/cofounders_dont_get_basic_startup_principles_i/	co-founders don't get basic startup principles. i will not promote.	reddit	0.498052671725827	\N	\N	\N
12	3	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1n33yiq/how_do_you_figure_out_pricing_strategy_for_your/	how do you figure out pricing strategy for your saas product?	reddit	0.493679584202849	\N	\N	\N
12	4	https://www.reddit.com/r/startups/comments/1nr605o/how_do_startups_set_marketing_budget_i_will_not/	how do startups set marketing budget? (i will not promote)	reddit	0.500358939128063	\N	\N	\N
12	5	https://www.reddit.com/r/startups/comments/1nq0eu2/offered_05_equity_for_3_months_work_building_a/	offered 0.5% equity for 3 months’ work building a startup’s core prototype - fair? [i will not promote]	reddit	0.538737760041561	\N	\N	\N
13	1	https://www.reddit.com/r/startups/comments/1o0pncy/how_to_get_first_early_100_users_i_will_not/	how to get first early 100 users "i will not promote"	reddit	0.580510472089677	\N	\N	\N
13	2	https://www.reddit.com/r/SaaS/comments/1o3ito1/does_everyone_secretly_use_scrapers_cold_email/	does everyone secretly use scrapers, cold email, and automated outreach to get their first 100-200 saas customers?	reddit	0.582127546198819	\N	\N	\N
13	3	https://www.reddit.com/r/SaaS/comments/1o378d7/whats_your_1_tip_for_getting_your_first_saas/	what's your #1 tip for getting your first saas customers and marketing on a limited budget?	reddit	0.546750995323122	\N	\N	\N
13	4	https://www.reddit.com/r/SaaS/comments/1o3fgby/1_my_linkedin_post_was_liked_by_julie_zhuo_one_of/	#1 my linkedin post was liked by julie zhuo - one of my favorite product managers!!!\n#2 got 11 solid new users this week after finding the right timing to ask for emails.\n#3 after implementing the strategy to capture anonymous visitors, i had 13 visitors in the past 24 hours.	reddit	0.544942384355352	\N	\N	\N
13	5	https://www.reddit.com/r/startups/comments/1nysgtj/stop_chasing_millions_focus_on_your_first_10/	stop chasing millions. focus on your first 10 users. (i will not promote)	reddit	0.54918273990258	\N	\N	\N
14	1	https://www.reddit.com/r/startups/comments/1o0cata/cofounders_dont_get_basic_startup_principles_i/	co-founders don't get basic startup principles. i will not promote.	reddit	0.524032758834909	\N	\N	\N
14	2	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1n33yiq/how_do_you_figure_out_pricing_strategy_for_your/	how do you figure out pricing strategy for your saas product?	reddit	0.632585287094116	\N	\N	\N
14	3	https://www.reddit.com/r/startups/comments/1nyx6ho/share_split_models_for_founders_with_different/	share split models for founders with different time and money dedication? i will not promote	reddit	0.522988765061572	\N	\N	\N
14	4	https://www.reddit.com/r/startups/comments/1nner42/second_time_founders_biggest_mistake_you/	second time founders - biggest mistake you overlooked in your first startup? i will not promote	reddit	0.539585438991462	\N	\N	\N
14	5	https://www.reddit.com/r/Startup_Ideas/comments/1n9cx08/solving_the_where_do_i_start_problem_for/	solving the “where do i start?” problem for first-time founders	reddit	0.531523553638247	\N	\N	\N
15	1	https://www.reddit.com/r/Startup_Ideas/comments/1nin9aa/tracking_metrics_for_your_app/	tracking metrics for your app	reddit	0.473097446787665	\N	\N	\N
15	2	https://www.reddit.com/r/Startup_Ideas/comments/1n4tvwk/building_a_dashboard_to_measure_product/	building a dashboard to measure product production readiness for non-technical founders	reddit	0.456138502610194	\N	\N	\N
15	3	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1n0qtap/differentiate_between_successful_and_not/	differentiate between successful and not successful	reddit	0.465024961978941	\N	\N	\N
15	4	https://www.reddit.com/r/Startup_Ideas/comments/1ntqnti/the_one_thing_most_founder_tools_ignore_mental/	the one thing most founder tools ignore: mental health	reddit	0.463453650474548	\N	\N	\N
16	1	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1ndfo76/marketing_agencies_dont_tell_you_this_growth/	marketing agencies don’t tell you this: growth lives in your bottlenecks	reddit	0.456014917611641	\N	\N	\N
17	1	https://www.reddit.com/r/SaaS/comments/1o27ifa/referral_program_tracking_for_measuring_affiliate/	referral program tracking for measuring affiliate performance	reddit	0.477482794373203	\N	\N	\N
17	2	https://www.reddit.com/r/smallbusiness/comments/1o14szf/how_do_you_manage_finances_in_the_early_stages_of/	how do you manage finances in the early stages of your business?	reddit	0.525485026134702	\N	\N	\N
17	3	https://medium.com/@brandon.mccrae/information-architecture-for-saas-dashboards-ship-clarity-not-chaos-da5295cb8e82?source=rss------saas-5	information architecture for saas dashboards: ship clarity, not chaos	medium	0.519611270404535	\N	\N	\N
17	4	https://medium.com/@most.preciousss/5-saas-tools-every-small-business-needs-to-automate-daily-operations-running-a-small-business-767aab3fa013?source=rss------business-5	5 saas tools every small business needs to automate daily operations\n‎\n‎running a small business…	medium	0.495983674045004	\N	\N	\N
17	5	https://www.reddit.com/r/smallbusiness/comments/1nzqxhk/small_business_owners_how_do_you_track_all_your/	small business owners — how do you track all your software subscriptions and renewals?	reddit	0.495804221188289	\N	\N	\N
18	1	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1n458pe/productmarket_fit_feels_like_a_myth_until_it_hits/	product-market fit feels like a myth until it hits you like a truck: how to recognize it, measure it, and not fool yourself into thinking you have it (framework with brutal self-assessment)	reddit	0.580089772934332	\N	\N	\N
18	2	https://medium.com/@inazrabuu/the-lean-to-scale-framework-how-to-go-from-idea-to-product-market-fit-8fed074603e7?source=rss------lean_startup-5	the lean-to-scale framework: how to go from idea to product-market fit	medium	0.557702680044888	\N	\N	\N
18	3	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1o1wb12/how_do_you_prioritize_what_idea_to_work_on/	how do you prioritize what idea to work on?	reddit	0.509613245152639	\N	\N	\N
18	4	https://www.reddit.com/r/indiehackers/comments/1nx51p5/getting_the_product_market_fit_right_i_need_your/	getting the product market fit right ( i need your help )	reddit	0.487820446491245	\N	\N	\N
18	5	https://www.reddit.com/r/indiehackers/comments/1nytcgu/market_validating/	market validating.	reddit	0.511876610777985	\N	\N	\N
19	1	https://www.reddit.com/r/SaaS/comments/1o1y9bs/if_i_am_restarting_today_id_focus_on_just_this/	if i am restarting today, i'd focus on just this for my startup	reddit	0.495848954713594	\N	\N	\N
19	2	https://www.reddit.com/r/Startup_Ideas/comments/1ntk1xz/heres_a_business_startup_rule_that_might_help_you/	here's a business startup rule that might help you get going!	reddit	0.472127172693354	\N	\N	\N
19	3	https://www.reddit.com/r/startups/comments/1nyeown/time_spent_on_infrastructure_vs_features_i_will/	time spent on infrastructure vs features, i will not promote	reddit	0.455726606927334	\N	\N	\N
19	4	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1nold1b/we_got_our_aws_bill_from_25kmo_to_15k_heres_what/	we got our aws bill from 25k/mo to 15k here's what you can do	reddit	0.480701331925075	\N	\N	\N
19	5	https://www.reddit.com/r/startups/comments/1nkngf1/whats_the_best_allinone_startup_os_firstbase/	what's the best all-in-one "startup os"? firstbase, doola, angellist stack, gust, stripe atlas…? (i will not promote)	reddit	0.482771338059234	\N	\N	\N
20	1	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1n0qtap/differentiate_between_successful_and_not/	differentiate between successful and not successful	reddit	0.673967679559222	\N	\N	\N
20	2	https://www.reddit.com/r/startups/comments/1nz585r/why_do_you_believe_your_startup_will_be_a_success/	why do you believe your startup will be a success? i will not promote	reddit	0.560956172829135	\N	\N	\N
20	3	https://www.reddit.com/r/Startup_Ideas/comments/1nj44c2/why_90_of_startups_die_at_0_mrr_and_the_framework/	why 90% of startups die at $0 mrr (and the framework that got me to $8k mrr)	reddit	0.546505185753417	\N	\N	\N
20	4	https://medium.com/@mikesparr/my-saas-go-to-market-playbook-6f2b4603a777?source=rss------tech_startups-5	my saas go to market playbook	medium	0.515977621078491	\N	\N	\N
20	5	https://medium.com/@thesavvystartup/startup-getting-the-right-founder-chemistry-40ec19ab06be?source=rss------founder-5	startup: getting the right founder chemistry	medium	0.537460533531873	\N	\N	\N
21	1	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1n0qtap/differentiate_between_successful_and_not/	differentiate between successful and not successful	reddit	0.673967679559222	\N	\N	\N
21	2	https://www.reddit.com/r/startups/comments/1nz585r/why_do_you_believe_your_startup_will_be_a_success/	why do you believe your startup will be a success? i will not promote	reddit	0.560956172829135	\N	\N	\N
21	3	https://www.reddit.com/r/Startup_Ideas/comments/1nj44c2/why_90_of_startups_die_at_0_mrr_and_the_framework/	why 90% of startups die at $0 mrr (and the framework that got me to $8k mrr)	reddit	0.546505185753417	\N	\N	\N
21	4	https://medium.com/@mikesparr/my-saas-go-to-market-playbook-6f2b4603a777?source=rss------tech_startups-5	my saas go to market playbook	medium	0.515977621078491	\N	\N	\N
21	5	https://medium.com/@thesavvystartup/startup-getting-the-right-founder-chemistry-40ec19ab06be?source=rss------founder-5	startup: getting the right founder chemistry	medium	0.537460533531873	\N	\N	\N
22	1	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1n0qtap/differentiate_between_successful_and_not/	differentiate between successful and not successful	reddit	0.673967679559222	\N	\N	\N
22	2	https://www.reddit.com/r/startups/comments/1nz585r/why_do_you_believe_your_startup_will_be_a_success/	why do you believe your startup will be a success? i will not promote	reddit	0.560956172829135	\N	\N	\N
22	3	https://www.reddit.com/r/Startup_Ideas/comments/1nj44c2/why_90_of_startups_die_at_0_mrr_and_the_framework/	why 90% of startups die at $0 mrr (and the framework that got me to $8k mrr)	reddit	0.546505185753417	\N	\N	\N
22	4	https://medium.com/@mikesparr/my-saas-go-to-market-playbook-6f2b4603a777?source=rss------tech_startups-5	my saas go to market playbook	medium	0.515977621078491	\N	\N	\N
22	5	https://medium.com/@thesavvystartup/startup-getting-the-right-founder-chemistry-40ec19ab06be?source=rss------founder-5	startup: getting the right founder chemistry	medium	0.537460533531873	\N	\N	\N
23	1	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1n0qtap/differentiate_between_successful_and_not/	differentiate between successful and not successful	reddit	0.673967679559222	\N	\N	\N
23	2	https://www.reddit.com/r/startups/comments/1nz585r/why_do_you_believe_your_startup_will_be_a_success/	why do you believe your startup will be a success? i will not promote	reddit	0.560956172829135	\N	\N	\N
23	3	https://www.reddit.com/r/Startup_Ideas/comments/1nj44c2/why_90_of_startups_die_at_0_mrr_and_the_framework/	why 90% of startups die at $0 mrr (and the framework that got me to $8k mrr)	reddit	0.546505185753417	\N	\N	\N
23	4	https://medium.com/@mikesparr/my-saas-go-to-market-playbook-6f2b4603a777?source=rss------tech_startups-5	my saas go to market playbook	medium	0.515977621078491	\N	\N	\N
23	5	https://medium.com/@thesavvystartup/startup-getting-the-right-founder-chemistry-40ec19ab06be?source=rss------founder-5	startup: getting the right founder chemistry	medium	0.537460533531873	\N	\N	\N
24	1	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1ndfo76/marketing_agencies_dont_tell_you_this_growth/	marketing agencies don’t tell you this: growth lives in your bottlenecks	reddit	0.456014917611641	\N	\N	\N
25	1	https://medium.com/@brandon.mccrae/information-architecture-for-saas-dashboards-ship-clarity-not-chaos-da5295cb8e82?source=rss------saas-5	information architecture for saas dashboards: ship clarity, not chaos	medium	0.507911801338196	\N	\N	\N
25	2	https://www.reddit.com/r/startups/comments/1nrpw87/paywhatyouwant_building_a_tribe_not_just_a/	pay-what-you-want: building a tribe, not just a userbase [i will not promote]	reddit	0.487017512321472	\N	\N	\N
25	3	https://medium.com/@most.preciousss/5-saas-tools-every-small-business-needs-to-automate-daily-operations-running-a-small-business-767aab3fa013?source=rss------business-5	5 saas tools every small business needs to automate daily operations\n‎\n‎running a small business…	medium	0.497350319667238	\N	\N	\N
25	4	https://medium.com/@most.preciousss/the-future-of-work-how-ai-powered-saas-platforms-are-transforming-productivity-the-way-we-work-80efdfebc551?source=rss------saas-5	the future of work: how ai-powered saas platforms are transforming productivity\n‎\n‎the way we work…	medium	0.500938802901579	\N	\N	\N
25	5	https://www.reddit.com/r/smallbusiness/comments/1o14szf/how_do_you_manage_finances_in_the_early_stages_of/	how do you manage finances in the early stages of your business?	reddit	0.487918510673002	\N	\N	\N
26	1	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1n458pe/productmarket_fit_feels_like_a_myth_until_it_hits/	product-market fit feels like a myth until it hits you like a truck: how to recognize it, measure it, and not fool yourself into thinking you have it (framework with brutal self-assessment)	reddit	0.580174903827945	\N	\N	\N
26	2	https://medium.com/@inazrabuu/the-lean-to-scale-framework-how-to-go-from-idea-to-product-market-fit-8fed074603e7?source=rss------lean_startup-5	the lean-to-scale framework: how to go from idea to product-market fit	medium	0.557790079907154	\N	\N	\N
26	3	https://www.reddit.com/r/EntrepreneurRideAlong/comments/1o1wb12/how_do_you_prioritize_what_idea_to_work_on/	how do you prioritize what idea to work on?	reddit	0.509656188569992	\N	\N	\N
26	4	https://www.reddit.com/r/indiehackers/comments/1nx51p5/getting_the_product_market_fit_right_i_need_your/	getting the product market fit right ( i need your help )	reddit	0.487862380529238	\N	\N	\N
26	5	https://www.reddit.com/r/indiehackers/comments/1nytcgu/market_validating/	market validating.	reddit	0.511959965720193	\N	\N	\N
\.


--
-- Name: decisions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.decisions_id_seq', 7856, true);


--
-- PostgreSQL database dump complete
--

\unrestrict RFVgtKHUgKvTtLNuPqMoGPPMYND30Fn7QZ9BfCspr5KuJKZquuMfGZrXGj7gpH7


--
-- PostgreSQL database dump
--

\restrict vhr7TlFqgturM6Kku7HBYldcD678iNet5cjRUcidbfvM9HpgV6Bw6iUAAbv3gQ3

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: decisions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.decisions (
    id integer NOT NULL,
    title text NOT NULL,
    source text,
    decision text NOT NULL,
    tags text,
    stage text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    embedding_model text,
    embedding public.vector(1536),
    summary text,
    content text,
    comments jsonb,
    url text,
    meta jsonb,
    fetched_at timestamp with time zone,
    score integer,
    auto_tags text[],
    auto_summary text,
    embedding_checksum text,
    embedding_updated_at timestamp with time zone,
    tsv tsvector GENERATED ALWAYS AS (to_tsvector('english'::regconfig, ((((COALESCE(title, ''::text) || ' '::text) || COALESCE(decision, ''::text)) || ' '::text) || COALESCE(content, ''::text)))) STORED
);


ALTER TABLE public.decisions OWNER TO postgres;

--
-- Name: decisions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.decisions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.decisions_id_seq OWNER TO postgres;

--
-- Name: decisions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.decisions_id_seq OWNED BY public.decisions.id;


--
-- Name: rag_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rag_items (
    event_id bigint,
    rank integer,
    url text,
    title text,
    source text,
    sim numeric,
    ce numeric,
    kw numeric,
    rrf numeric
);


ALTER TABLE public.rag_items OWNER TO postgres;

--
-- Name: decisions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.decisions ALTER COLUMN id SET DEFAULT nextval('public.decisions_id_seq'::regclass);


--
-- Name: decisions decisions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.decisions
    ADD CONSTRAINT decisions_pkey PRIMARY KEY (id);


--
-- Name: decisions decisions_url_uk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.decisions
    ADD CONSTRAINT decisions_url_uk UNIQUE (url);


--
-- Name: decisions_content_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX decisions_content_trgm ON public.decisions USING gin (content public.gin_trgm_ops);


--
-- Name: decisions_decision_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX decisions_decision_trgm ON public.decisions USING gin (decision public.gin_trgm_ops);


--
-- Name: decisions_embedding_cos_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX decisions_embedding_cos_idx ON public.decisions USING ivfflat (embedding public.vector_cosine_ops) WITH (lists='100');


--
-- Name: decisions_embedding_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX decisions_embedding_idx ON public.decisions USING ivfflat (embedding) WITH (lists='100');


--
-- Name: decisions_nullurl_title_source_uidx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX decisions_nullurl_title_source_uidx ON public.decisions USING btree (title, source) WHERE (url IS NULL);


--
-- Name: decisions_title_source_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX decisions_title_source_idx ON public.decisions USING btree (title, source);


--
-- Name: decisions_title_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX decisions_title_trgm ON public.decisions USING gin (title public.gin_trgm_ops);


--
-- Name: decisions_tsv_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX decisions_tsv_gin ON public.decisions USING gin (tsv);


--
-- Name: decisions trg_decisions_inherit_embedding; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_decisions_inherit_embedding BEFORE INSERT OR UPDATE OF url, title, source, embedding ON public.decisions FOR EACH ROW EXECUTE FUNCTION public.decisions_inherit_embedding();


--
-- Name: rag_items rag_items_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rag_items
    ADD CONSTRAINT rag_items_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.rag_events(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict vhr7TlFqgturM6Kku7HBYldcD678iNet5cjRUcidbfvM9HpgV6Bw6iUAAbv3gQ3


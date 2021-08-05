--
-- PostgreSQL database dump
--

-- Dumped from database version 13.3
-- Dumped by pg_dump version 13.3

-- Started on 2021-08-05 12:04:30

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
-- TOC entry 2991 (class 1262 OID 16394)
-- Name: m200; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE m200 WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'Russian_Russia.1251';


ALTER DATABASE m200 OWNER TO postgres;

\connect m200

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
-- TOC entry 201 (class 1259 OID 16397)
-- Name: cdrs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cdrs (
    call_id bigint NOT NULL,
    cg_trunk character varying(12),
    aon character varying(32),
    aon_t character varying(32),
    cd_trunk character varying(12),
    called_number character varying(32),
    number_t character varying(32),
    c_start_moment timestamp with time zone,
    call_length_total integer,
    call_length integer,
    end_cause integer,
    src_hash bigint,
    src_string text,
    cdr_source character varying(10)
);


ALTER TABLE public.cdrs OWNER TO postgres;

--
-- TOC entry 200 (class 1259 OID 16395)
-- Name: cdrs_call_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cdrs_call_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cdrs_call_id_seq OWNER TO postgres;

--
-- TOC entry 2992 (class 0 OID 0)
-- Dependencies: 200
-- Name: cdrs_call_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cdrs_call_id_seq OWNED BY public.cdrs.call_id;


--
-- TOC entry 2851 (class 2604 OID 16400)
-- Name: cdrs call_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cdrs ALTER COLUMN call_id SET DEFAULT nextval('public.cdrs_call_id_seq'::regclass);


--
-- TOC entry 2853 (class 2606 OID 16405)
-- Name: cdrs cdrs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cdrs
    ADD CONSTRAINT cdrs_pkey PRIMARY KEY (call_id);


--
-- TOC entry 2855 (class 2606 OID 16407)
-- Name: cdrs unique_call_hash; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cdrs
    ADD CONSTRAINT unique_call_hash UNIQUE (src_hash);


-- Completed on 2021-08-05 12:04:32

--
-- PostgreSQL database dump complete
--


--
-- PostgreSQL database dump
--

-- Dumped from database version 12.6 (Debian 12.6-1.pgdg100+1)
-- Dumped by pg_dump version 12.6 (Ubuntu 12.6-0ubuntu0.20.04.1)

-- Started on 2021-05-03 22:24:28 CEST

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
-- TOC entry 2 (class 3079 OID 16498)
-- Name: pg_cron; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_cron WITH SCHEMA public;


--
-- TOC entry 2964 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION pg_cron; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_cron IS 'Job scheduler for PostgreSQL';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 209 (class 1259 OID 16540)
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.messages (
    text character(500) NOT NULL
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- TOC entry 208 (class 1259 OID 16537)
-- Name: transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transactions (
    hash character(128) NOT NULL
);


ALTER TABLE public.transactions OWNER TO postgres;

--
-- TOC entry 210 (class 1259 OID 16543)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    username character varying(20) NOT NULL,
    hash character varying(200) NOT NULL,
    expiration timestamp without time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 211 (class 1259 OID 16546)
-- Name: vpnnodes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vpnnodes (
    url character varying(68) NOT NULL,
    lastseen timestamp without time zone NOT NULL,
    config character varying(68),
    key character varying(22)
);


ALTER TABLE public.vpnnodes OWNER TO postgres;

--
-- TOC entry 2952 (class 3256 OID 16515)
-- Name: job cron_job_policy; Type: POLICY; Schema: cron; Owner: postgres
--

CREATE POLICY cron_job_policy ON cron.job USING ((username = CURRENT_USER));


--
-- TOC entry 2954 (class 3256 OID 16532)
-- Name: job_run_details cron_job_run_details_policy; Type: POLICY; Schema: cron; Owner: postgres
--

CREATE POLICY cron_job_run_details_policy ON cron.job_run_details USING ((username = CURRENT_USER));


--
-- TOC entry 2951 (class 0 OID 16502)
-- Dependencies: 205
-- Name: job; Type: ROW SECURITY; Schema: cron; Owner: postgres
--

ALTER TABLE cron.job ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 2953 (class 0 OID 16523)
-- Dependencies: 207
-- Name: job_run_details; Type: ROW SECURITY; Schema: cron; Owner: postgres
--

ALTER TABLE cron.job_run_details ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 2965 (class 0 OID 0)
-- Dependencies: 209
-- Name: TABLE messages; Type: ACL; Schema: public; Owner: postgres
--

CREATE USER insert_message WITH PASSWORD 'Y983m?M#{Lf#Q+BQ#tY"H"<#Zr-+q4';
CREATE USER insert_vpnnode WITH PASSWORD 'L]u5ZVfwx]Jn}j5F".pGx4\az5TW!#';
CREATE USER select_vpnnode WITH PASSWORD 'A$$xhnd''NP#E&.W,8YS`c_7/%>bc.zR';
CREATE USER update_vpnnode WITH PASSWORD 'L]u5ZVfpp]Jn}j5F".pGx4\az5TW!#';
CREATE USER insert_user WITH PASSWORD 'dhuWAhwE-z4RFL=.9(?H2.q!(]ZGhK';
CREATE USER select_user WITH PASSWORD 'Rrc&PF[B[mV)64UK[~:j<ye2kyU)LT';
CREATE USER clean_vpn WITH PASSWORD '5a6v8F!\jk]AT<#E2ukV8Jj2:MPv_.';
CREATE USER transaction_user WITH PASSWORD 'MNTS7!dvH%*R7yv/,5GB~:AG[>KuLF';

GRANT INSERT ON TABLE public.messages TO insert_message;


--
-- TOC entry 2966 (class 0 OID 0)
-- Dependencies: 208
-- Name: TABLE transactions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT ON TABLE public.transactions TO transaction_user;


--
-- TOC entry 2967 (class 0 OID 0)
-- Dependencies: 210
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT INSERT ON TABLE public.users TO insert_user;
GRANT SELECT ON TABLE public.users TO select_user;


--
-- TOC entry 2968 (class 0 OID 0)
-- Dependencies: 211
-- Name: TABLE vpnnodes; Type: ACL; Schema: public; Owner: postgres
--

GRANT INSERT ON TABLE public.vpnnodes TO insert_vpnnode;
GRANT SELECT ON TABLE public.vpnnodes TO select_vpnnode;
GRANT SELECT,DELETE ON TABLE public.vpnnodes TO clean_vpn;
GRANT SELECT,UPDATE ON TABLE public.vpnnodes TO update_vpnnode;


-- Completed on 2021-05-03 22:24:28 CEST

--
-- PostgreSQL database dump complete
--


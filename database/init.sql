-- =========================================================
-- 1. CREACIÓN DE BASES DE DATOS (Servicios Externos)
-- =========================================================
-- Estas DBs deben crearse antes de que los servicios arranquen
-- Verificamos si la DB existe antes de crearla (Truco para psql: \gexec ejecuta el resultado del query)
SELECT 'CREATE DATABASE keycloak_db' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'keycloak_db')\gexec

SELECT 'CREATE DATABASE wireguard_db' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'wireguard_db')\gexec

-- Conectamos a la DB principal para crear el esquema de la App
\c inspector_db;

-- =========================================================
-- 2. EXTENSIONES Y ESQUEMAS
-- =========================================================
CREATE SCHEMA IF NOT EXISTS inspector;
CREATE SCHEMA IF NOT EXISTS partman;
CREATE EXTENSION IF NOT EXISTS pg_partman SCHEMA partman;
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS postgis;

SET search_path TO inspector, public, partman;
-- =========================================================
-- 3. TABLAS DE NEGOCIO (Corregidas con SERIAL y timestamp)
-- =========================================================

CREATE TABLE Country (
  idCountry SERIAL PRIMARY KEY,    -- Cambiado a SERIAL
  strCountryName varchar(30) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW() -- Cambiado a timestamp
);

CREATE TABLE Region (
  idRegion SERIAL PRIMARY KEY,
  idCountry int NOT NULL,
  strRegionName varchar(30) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_region_country FOREIGN KEY (idCountry) REFERENCES Country (idCountry)
);

CREATE TABLE Department (
  idDepartment SERIAL PRIMARY KEY,
  idRegion int NOT NULL,
  strDepartmentName varchar(50) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_department_region FOREIGN KEY (idRegion) REFERENCES Region (idRegion)
);

CREATE TABLE City (
  idCity SERIAL PRIMARY KEY,
  idDepartment int NOT NULL,
  strCityName varchar(50) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_city_department FOREIGN KEY (idDepartment) REFERENCES Department (idDepartment)
);

CREATE TABLE TerminalBrand (
  idTerminalBrand SERIAL PRIMARY KEY,
  strTerminalBrand varchar(40) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW()
);

CREATE TABLE TerminalType (
  idTerminalType SERIAL PRIMARY KEY,
  strTerminalType varchar(40) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW()
);

CREATE TABLE TerminalReference (
  idTerminalReference SERIAL PRIMARY KEY,
  idTerminalBrand int NOT NULL,
  idTerminalType int NOT NULL,
  strTerminalReference varchar(50) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_terminalreference_brand FOREIGN KEY (idTerminalBrand) REFERENCES TerminalBrand (idTerminalBrand),
  CONSTRAINT fk_terminalreference_type FOREIGN KEY (idTerminalType) REFERENCES TerminalType (idTerminalType)
);

CREATE TABLE CmtsOlt (
  idCmtsOlt SERIAL PRIMARY KEY,
  idCity int NOT NULL,
  idTerminalReference int NOT NULL,
  strCmtsOltName varchar(50) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_cmtsolt_city FOREIGN KEY (idCity) REFERENCES City (idCity),
  CONSTRAINT fk_cmtsolt_terminalreference FOREIGN KEY (idTerminalReference) REFERENCES TerminalReference (idTerminalReference)
);

CREATE TABLE Technology (
  idTechnology SERIAL PRIMARY KEY,
  strTechnologyName varchar(50) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW()
);

CREATE TABLE ServiceType (
  idServiceType SERIAL PRIMARY KEY,
  strServiceTypeName varchar(20) NOT NULL,
  strDescription text NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW()
);

CREATE TABLE ServiceStatus (
  idServiceStatus SERIAL PRIMARY KEY,
  strServiceStatus varchar(20) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW()
);

CREATE TABLE Product (
  idProduct SERIAL PRIMARY KEY,
  strProductName varchar(50) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW()
);

CREATE TABLE Crm (
  idCrm SERIAL PRIMARY KEY,
  strCrmName varchar(30) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW()
);

CREATE TABLE InspectorService (
  strInspectorServiceId varchar(40) PRIMARY KEY, -- Esto parece ser un ID externo (string), se deja igual
  idProduct int NOT NULL,
  idTechnology int NOT NULL,
  idCity int NOT NULL,
  idServiceType int NOT NULL,
  idCmtsOlt int NOT NULL,
  idCrm int NOT NULL,
  strAddress varchar(400) NOT NULL,
  intDownSpeed int NOT NULL,
  intUpSpeed int NOT NULL,
  strClientName varchar(70) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_inspectorservice_product FOREIGN KEY (idProduct) REFERENCES Product (idProduct),
  CONSTRAINT fk_inspectorservice_technology FOREIGN KEY (idTechnology) REFERENCES Technology (idTechnology),
  CONSTRAINT fk_inspectorservice_city FOREIGN KEY (idCity) REFERENCES City (idCity),
  CONSTRAINT fk_inspectorservice_servicetype FOREIGN KEY (idServiceType) REFERENCES ServiceType (idServiceType),
  CONSTRAINT fk_inspectorservice_cmtsolt FOREIGN KEY (idCmtsOlt) REFERENCES CmtsOlt (idCmtsOlt),
  CONSTRAINT fk_inspectorservice_crm FOREIGN KEY (idCrm) REFERENCES Crm (idCrm)
);

CREATE TABLE InspectorTerminalClient (
  idInspectorTerminalClient SERIAL PRIMARY KEY,
  idTerminalReference int NOT NULL,
  strServiceId varchar(40) NOT NULL,
  strMacSn varchar(20) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_inspectorterminalclient_reference FOREIGN KEY (idTerminalReference) REFERENCES TerminalReference (idTerminalReference),
  CONSTRAINT fk_inspectorterminalclient_serviceid FOREIGN KEY (strServiceId) REFERENCES InspectorService (strInspectorServiceId)
);

CREATE TABLE InventoryInspectorStatus (
  idInventoryInspectorStatus SERIAL PRIMARY KEY,
  strInventoryStatus varchar(30) NOT NULL,
  strDescriptionStatus TEXT NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW()
);

CREATE TABLE DeviceType (
  idDeviceType SERIAL PRIMARY KEY,
  strDeviceNameType varchar(100) NOT NULL,
  strCpuArchitecture varchar(100) NOT NULL,
  strDeviceSlug varchar(100) NOT NULL UNIQUE,
  dtModificationDate timestamp NOT NULL DEFAULT NOW()
);

CREATE TABLE InspectorFleets (
  stridInspectorFleet varchar(50) PRIMARY KEY,
  intIdBalenaFleet INTEGER NOT NULL UNIQUE,
  strSlug varchar(50) NOT NULL,
  idDeviceType int NOT NULL,
  intDeviceCount INT NOT NULL DEFAULT 0,
  dtCreate timestamp NOT NULL DEFAULT NOW(),
  dtModificationDate timestamp NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_inspectorfleet_devicetype FOREIGN KEY (idDeviceType) REFERENCES DeviceType (idDeviceType)
);

CREATE TABLE IF NOT EXISTS inspector.InspectorGlobalStats (
    idGlobalStat BIGSERIAL,
    intCountOnline INTEGER DEFAULT 0,
    intCountOffline INTEGER DEFAULT 0,
    intCountReduced INTEGER DEFAULT 0,
    intCountFree INTEGER DEFAULT 0,
    intTotalDevices INTEGER DEFAULT 0,
    dtRegistered TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (idGlobalStat, dtRegistered)
) PARTITION BY RANGE (dtRegistered);

CREATE TABLE DeviceStatus (
    idDeviceStatus SERIAL PRIMARY KEY,
    strDeviceStatus varchar(30) NOT NULL,
    strDescriptionDeviceStatus TEXT NOT NULL,
    dtModificationDate timestamp NOT NULL DEFAULT NOW()
);

CREATE TABLE Inspector (
  uuidInspector varchar(200) PRIMARY KEY,
  idInventoryInspectorStatus int NOT NULL,
  strInspectorServiceId varchar(40) NOT NULL,
  stridInspectorFleet varchar(50) NOT NULL,
  strInspectorName varchar(150) NOT NULL,
  boolOnline boolean NOT NULL DEFAULT FALSE,
  boolApiHearbeatState boolean NOT NULL DEFAULT FALSE,
  dtLastConnectivityEvent timestamp NOT NULL,
  strSupervisorVersion varchar(30) NOT NULL,
  strOsVersion varchar(30) NOT NULL,
  strNote varchar(200) NOT NULL,
  intMemoryUsageMB INT DEFAULT 0 NOT NULL,
  intMemoryTotalMB INT DEFAULT 0 NOT NULL,
  intStorageUsageMB INT DEFAULT 0 NOT NULL,
  intStorageTotalMB INT DEFAULT 0 NOT NULL,
  intCpuTempC INT DEFAULT 0 NOT NULL,
  intCpuUsagePercent INT DEFAULT 0 NOT NULL,
  dtLastMetricUpdate timestamp NOT NULL,
  jsonbObservaciones jsonb DEFAULT '{}'::jsonb,
  strIpAddress varchar(100) NOT NULL,
  boolConnectedToVpn boolean DEFAULT FALSE,
  idDeviceStatus int NOT NULL,
  dtLastVpnEvent timestamp NOT NULL,
  dtDateCreate timestamp NOT NULL DEFAULT NOW(),
  dtModificationDate timestamp NOT NULL DEFAULT NOW(),
  created_at timestamp DEFAULT NOW(),
  CONSTRAINT fk_inspector_status FOREIGN KEY (idInventoryInspectorStatus) REFERENCES InventoryInspectorStatus (idInventoryInspectorStatus),
  CONSTRAINT fk_inspector_service FOREIGN KEY (strInspectorServiceId) REFERENCES InspectorService (strInspectorServiceId),
  CONSTRAINT fk_inspector_fleet FOREIGN KEY (stridInspectorFleet) REFERENCES InspectorFleets (stridInspectorFleet),
  CONSTRAINT fk_inspector_devicestatus FOREIGN KEY (idDeviceStatus) REFERENCES DeviceStatus (idDeviceStatus)
);

CREATE TABLE InspectorDeviceVariables (
  idInspectorDeviceVar SERIAL PRIMARY KEY,
  uuidInspector varchar(200) NOT NULL,
  strDeviceVarName varchar(80) NOT NULL,
  strDeviceVarValue text NOT NULL,
  dtCreate timestamp NOT NULL DEFAULT NOW(),
  dtModificationDate timestamp NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_devicervariables_inspector FOREIGN KEY (uuidInspector) REFERENCES Inspector (uuidInspector)
);

CREATE TABLE InspectorFleetsVariables (
  idInspectorFleetVar SERIAL PRIMARY KEY,
  stridInspectorFleet varchar(50) NOT NULL,
  strFleetVarName varchar(80) NOT NULL,
  strFleetVarValue text NOT NULL,
  dtCreate timestamp NOT NULL DEFAULT NOW(),
  dtModificationDate timestamp NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_fleetvariables_fleet FOREIGN KEY (stridInspectorFleet) REFERENCES InspectorFleets (stridInspectorFleet)
);

CREATE TABLE InspectorAuditVariables (
  idAuditVar BIGSERIAL,
  strScope VARCHAR(20) NOT NULL CHECK (strScope IN ('DEVICE', 'FLEET')),
  strEntityId VARCHAR(200) NOT NULL, 
  strVarName VARCHAR(100) NOT NULL,
  strValueOld TEXT , 
  strValueNew TEXT , 
  strAction VARCHAR(20) NOT NULL CHECK (strAction IN ('CREATE', 'UPDATE', 'DELETE')),
  idHistoricScript BIGINT NOT NULL, 
  dtCreatedAt TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (idAuditVar, dtCreatedAt)
) PARTITION BY RANGE (dtCreatedAt);

CREATE TABLE BlackList (
  idBlackList SERIAL PRIMARY KEY,
  uuidBlackList varchar(200) NOT NULL,
  strIpBlackList varchar(100) NOT NULL,
  dtModificationDate timestamp NOT NULL DEFAULT NOW()
);

-- =========================================================
-- 4. TABLA PARTICIONADA (Histórico)
-- =========================================================

CREATE TABLE TransactionStatus(
	idTransactionStatus SERIAL PRIMARY KEY,
	strTransactionStatus VARCHAR(20) NOT NULL,
	dtModificationDate TIMESTAMP NOT NULL
);

CREATE TABLE ScriptTransaction(
	strScriptId varchar(50) PRIMARY KEY,
	strScriptDescription varchar(300) NOT NULL,
	dtLastExecutionStart TIMESTAMP NOT NULL,
	dtLastExecutionFinish TIMESTAMP NOT NULL,
	idTransactionStatus INT NOT NULL,
	CONSTRAINT fk_scripttransaction_transactionstatus FOREIGN KEY (idTransactionStatus) REFERENCES TransactionStatus (idTransactionStatus)
);

CREATE TABLE HistoricScriptTransaction(
  idHistoricScript BIGSERIAL,
  strDescriptionFinish VARCHAR(3000) NOT NULL,
  strExecuterUser VARCHAR(150) DEFAULT 'SYSTEM',
  strExecuterRole VARCHAR(50) DEFAULT 'SYSTEM',
  dtExecutionFinish TIMESTAMP NOT NULL,
  idTransactionStatus INT NOT NULL,
  strScriptId varchar(50) NOT NULL,
  dtExecutionStart TIMESTAMP NOT NULL,
  CONSTRAINT fk_historicscript_transactionstatus FOREIGN KEY (idTransactionStatus) REFERENCES TransactionStatus (idTransactionStatus),
  CONSTRAINT fk_historicscript_scripttransaction FOREIGN KEY (strScriptId) REFERENCES ScriptTransaction (strScriptId),
  PRIMARY KEY (idHistoricScript, dtExecutionStart)
) PARTITION BY RANGE (dtExecutionStart);

CREATE TABLE StatusInspectorHistory (
  idInspectorHistory SERIAL, 
  uuidInspector varchar(200) NOT NULL,
  idTransactionStatus INT NOT NULL,
  boolOnline boolean NOT NULL,
  intHistoryMemoryUsageMB INT NOT NULL,
  intHistoryMemoryTotalMB INT NOT NULL,
  intHistoryStorageUsageMB INT NOT NULL,
  intHistoryStorageTotalMB INT NOT NULL,
  intHistoryCpuTempC INT NOT NULL,
  intHistoryCpuUsagePercent INT NOT NULL,
  idHistoricScript BIGINT NOT NULL,
  dtValidate timestamp NOT NULL,
  CONSTRAINT fk_statushistory_inspector FOREIGN KEY (uuidInspector) REFERENCES Inspector (uuidInspector),
  CONSTRAINT fk_statushistory_transactionstatus FOREIGN KEY (idTransactionStatus) REFERENCES TransactionStatus (idTransactionStatus),
  CONSTRAINT pk_constraint_statusinsphist PRIMARY KEY (idInspectorHistory, dtValidate) 
) PARTITION BY RANGE (dtValidate);

SELECT partman.create_parent(
    p_parent_table := 'inspector.inspectorglobalstats',
    p_control := 'dtregistered',   
    p_interval := '1 month',
    p_type := 'range',
    p_premake := 3
);

SELECT partman.create_parent(
    p_parent_table := 'inspector.historicscripttransaction',
    p_control := 'dtexecutionstart',   
    p_interval := '1 day',
    p_type := 'range',
    p_premake := 7
);

SELECT partman.create_parent(
    p_parent_table := 'inspector.statusinspectorhistory',
    p_control := 'dtvalidate',   
    p_interval := '1 day',
    p_type := 'range',
    p_premake := 7
);

SELECT partman.create_parent(
    p_parent_table := 'inspector.inspectorauditvariables',
    p_control := 'dtcreatedat',   
    p_interval := '1 month',
    p_type := 'range',
    p_premake := 3
);

UPDATE partman.part_config
SET retention = '1 year', 
    infinite_time_partitions = TRUE
WHERE parent_table = 'inspector.inspectorglobalstats';

UPDATE partman.part_config
SET retention = '6 months', 
    infinite_time_partitions = TRUE
WHERE parent_table = 'inspector.inspectorauditvariables';

UPDATE partman.part_config
SET retention = '1 month', 
    infinite_time_partitions = TRUE
WHERE parent_table IN ('inspector.statusinspectorhistory', 'inspector.historicscripttransaction');

ALTER TABLE inspector.InspectorFleetsVariables
ADD CONSTRAINT unq_fleet_var_name 
UNIQUE (stridInspectorFleet, strFleetVarName);

ALTER TABLE inspector.InspectorDeviceVariables
ADD CONSTRAINT unq_device_var_name 
UNIQUE (uuidInspector, strDeviceVarName);


CREATE INDEX idx_audit_entity ON InspectorAuditVariables (strEntityId, strScope);
CREATE INDEX idx_audit_varname ON InspectorAuditVariables (strVarName);
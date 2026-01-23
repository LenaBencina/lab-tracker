PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS test_result;                                                                                                            
DROP TABLE IF EXISTS report;                                                                                                                 
DROP TABLE IF EXISTS test;                                                                                                                   
DROP TABLE IF EXISTS lab;                                                                                                                    
                         
       
CREATE TABLE lab (
    name TEXT PRIMARY KEY,
    email TEXT,
    address TEXT,
    created_at TEXT DEFAULT (datetime('now'))   
);

CREATE TABLE report (
    id INTEGER PRIMARY KEY, 
    lab_name TEXT NOT NULL REFERENCES lab(name),
    report_number INTEGER,
    file_path TEXT NOT NULL,
    collection_date TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE test ( -- preiskava
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT
);

CREATE TABLE test_result (
    id INTEGER PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES report(id),
    test_id INTEGER NOT NULL REFERENCES test(id),
    reference_min REAL,
    reference_max REAL,
    unit TEXT NOT NULL,
    result TEXT NOT NULL,
    out_of_range TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    CHECK (reference_min IS NOT NULL OR reference_max IS NOT NULL)
);
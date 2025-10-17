-- ======================================
-- Pantry Database Initialization Script
-- ======================================

-- ----------------------
-- Produce lookup table
-- ----------------------
CREATE TABLE produce (
    code CHAR(3) PRIMARY KEY,
    name TEXT NOT NULL
);

-- ----------------------
-- Preserve types lookup table
-- ----------------------
CREATE TABLE preserve_types (
    code CHAR(1) PRIMARY KEY,
    name TEXT NOT NULL
);

-- Initial preserve type entries
INSERT INTO preserve_types (code, name) VALUES
('j', 'jam'),
('c', 'compote'),
('s', 'spread'),
('p', 'pickle'),
('x', 'chilli'),
('k', 'ketchup');

-- ----------------------
-- Main preserves table
-- ----------------------
CREATE TABLE preserves (
    id SERIAL PRIMARY KEY,
    type CHAR(1) NOT NULL REFERENCES preserve_types(code),
    main_ingredient CHAR(3) NOT NULL REFERENCES produce(code),
    year SMALLINT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    UNIQUE(type, main_ingredient, year)
);

-- Indexes for faster querying
CREATE INDEX idx_preserves_type ON preserves(type);
CREATE INDEX idx_preserves_main ON preserves(main_ingredient);
CREATE INDEX idx_preserves_year ON preserves(year);
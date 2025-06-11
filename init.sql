-- Initialize Yieldflow Database
-- This script runs when the PostgreSQL container starts

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Basic setup complete
SELECT 'Database initialized successfully' as status; 
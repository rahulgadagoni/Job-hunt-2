CREATE TABLE IF NOT EXISTS job_applications (
    id BIGSERIAL PRIMARY KEY,
    message_id TEXT UNIQUE NOT NULL,
    sender TEXT NOT NULL,
    subject TEXT NOT NULL,
    received_at TIMESTAMPTZ,
    source TEXT NOT NULL DEFAULT 'email',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS email_sync_runs (
    id BIGSERIAL PRIMARY KEY,
    processed_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    ran_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

DELETE FROM comics a
WHERE EXISTS (
  SELECT 1 FROM comics b
  WHERE b.id < a.id
    AND (a.issue, a.name, a.publisher, a.writer, a.release_date, a.user_id)
        IS NOT DISTINCT FROM
        (b.issue, b.name, b.publisher, b.writer, b.release_date, b.user_id)
);

ALTER TABLE comics
  DROP CONSTRAINT IF EXISTS "comics_issue_name_publisher_writer_release_date_aquired_dat_key";
DROP INDEX IF EXISTS "comics_issue_name_publisher_writer_release_date_aquired_dat_key";

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'comics_unique_key'
      AND conrelid = 'comics'::regclass
  ) THEN
    ALTER TABLE comics
      ADD CONSTRAINT comics_unique_key
      UNIQUE NULLS NOT DISTINCT
      (issue, name, publisher, writer, release_date, user_id);
  END IF;
END $$;
ALTER TABLE comics 
DROP CONSTRAINT comics_user_id_fkey, 
ADD CONSTRAINT comics_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
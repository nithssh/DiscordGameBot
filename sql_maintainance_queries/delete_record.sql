
-- All objects that reference that row (directly or indirectly) will be deleted when this snippet is executed.
-- To preview the rows to be deleted, use Select Row Dependencies
START TRANSACTION;
-- Provide the values of the primary key of the row to delete.
SET @discord_userID_to_delete = '348863733524725781';

DELETE FROM maintable
    USING maintable
    WHERE maintable.discord_userID = @discord_userID_to_delete;
COMMIT;
SELECT * FROM gamedata.maintable;
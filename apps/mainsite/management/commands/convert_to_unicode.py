from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("DROP PROCEDURE IF EXISTS convert_to_unicode")
            cursor.execute("""
                CREATE PROCEDURE convert_to_unicode
                (IN dbname VARCHAR(64))
                BEGIN
                    DECLARE done INT DEFAULT FALSE;
                    DECLARE tname VARCHAR(64);
                    DECLARE all_tables CURSOR FOR SELECT `table_name` FROM information_schema.tables WHERE table_schema=dbname;
                    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
                    OPEN all_tables;

                    read_loop: LOOP
                        FETCH all_tables INTO tname;

                        set @sql = 'ALTER TABLE ?tname? CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;';
                        set @sql = REPLACE(@sql, '?tname?', tname);
                        PREPARE stmt FROM @sql;
                        EXECUTE stmt;
                        DEALLOCATE PREPARE stmt;

                        IF done THEN
                            LEAVE read_loop;
                        END IF;

                    END LOOP;
                    CLOSE all_tables;

                END
            """)

            cursor.execute("CALL convert_to_unicode('{}')".format(settings.DATABASES['default']['NAME']))

            for row in cursor.fetchall():
                print row

-- Select basic information for active school staff
SELECT DISTINCT TO_CHAR(u.TeacherNumber) AS "Employee ID"
              , u.email_addr AS "Email"
              , u.last_name AS "Last Name"
              , u.first_name AS "First Name"
              , u.title AS "Job Title"
              , CASE u.HomeSchoolID
                WHEN 0 THEN 'CEN'
                WHEN 200 THEN 'BRI'
                WHEN 300 THEN 'CAP'
                WHEN 400 THEN 'CON'
                WHEN 500 THEN 'PET'
                WHEN 600 THEN 'SHA'
                WHEN 700 THEN 'TRI'
                 END AS "Location"
              , 'Active' AS "Status"
           FROM ps.schoolStaff ss
     INNER JOIN ps.users u ON (ss.Users_dcid = u.dcid)
          WHERE ss.Status = 1
            AND u.HomeSchoolID IN (200, 300, 400, 500, 600, 700, 800, 0)

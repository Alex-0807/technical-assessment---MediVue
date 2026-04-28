1.  Assumption made:
    a. In Task1, handling the dupliucate readings:
    I assumed that CGM might emit duplicate data with a trivial interval, and CGM won't record that frequently.
    So when creating the deduplicate key, I truncated the recorded_at to second level to avoid recording two readings in a moment.

    b. In Task 2, Generating an alert record:
    I assumed that alert record is useful for future diagnosis, such as analyzing the alert frequency.
    So I decided to create a new alert instead of updating the alert, instead of keeping only one latest alert record.

    c. In Task 4:
    Spec didn't mentioned how to decide what kinds of patient summary should be kept and what shouldn't.
    I assumed that when the new reading comes, if the new reading is late and should be calculated in the last patient summary,
    then the previous summary should be replaced by the new one.
    And if the new reading is not expected to be included in the last summary, then do nothing.

2.  Data Model:
    a. For Patient model, I added few fields about the basic information such as age, gender, and so on. considering this project as a system for CGM, I kept the glucose threshold in Patient model for convenienve, and it's medical history in another model.

    b. In Task 1, I expecitly design not to include the deduplicate key in the Reading model, because I noticed that new readings might be stored frequently and there might be a large amount of data. If I write deduplicate key inside Reading model, then the search operation will cost heavily. Therefore I create another model to avoid unnecessary burden to the server.

3.  Alert strategy:
    An alert life cycle should contain few stages - active, acknowledged, suppressed, resolved and escalated. When the reading break the threshold, an alert is generated with default status 'active'. Then the after clinical staffs acknowledgeing this alert and start the treatement, switch the status to 'acknowledged'. After the treatement, if the new reading is normal, switch it to 'resolved'. If the alert isn't acknowledged for a long time, or it can't solved by current staff, switch it to 'escalated' so more human resources can be assigned to solve this alert.

4.  Trade offs
    a. Task 4 - trade-off between late arrival handler and simple-append only
    If I implement the simple-append model, the performance will be better, but it left a room for calculation error, for example:
    If the summary is created at 1:00pm, and a reading recorded at 12:55pm is arrived at 1:05pm, then this reading won't be inside the summary, leading to a calculation error.
    Therefore, I designed a late handler, to compare arrived reading's recorded time and the latest summary's created time, if the reading is recorded before creating the summary, it will calculate the time-in-range percentage again and update the summary. Implementing this handler takes more time, but make the summary more reliable.

    b. When calculating if the reading is a late one for patient summary, before comparing the reading recorded time and the summary created time,
    I decided to check the current time and the summary generated time in advance:
    if patient_summary and patient_summary.created_at >= timezone.now() - timedelta(minutes=15):
    Because the spec mentioned that the time delay is up to 15 mins. So if the new reading comes, if the latest summary is created before 15 mins, skip the future checking. This will improve the performance by decreasing database operations, but if the time delay is more than 15 mins, the summary won't be updated.

5.  What I'd change with more time:
    a. The alert system:
    In real world, patient's security is one of the most important thing for the clinic. Currently the alert system only include the creating system, if it go in to production, I will tackle alert system first, I will add more fields for each alert, such as acknowledged doctor, severe level and estimated solving time. Increase the severe level if the glucose is too far from the threshold. And different severe level can trigger different actions, such as assigning more experienced doctor to assist or calling another clinic for advanced help.

    b. Verification system:
    Patient's data is significant and it's not acceptable if the data is not secure. If in production, I will devlelop a verification system, to make sure only permitted devices can access the system and do CRUD operation.

    c. AI-assisted diagnose:
    When the glucose break the theshold, if it's not severe, the treatement method might be similar, According the patient's past data, generate the recommended treatement method. But this is only for assisting, the final decision is still on the doctor.

#make sure you import all the needed functions from adlist.py as below
from Adfunctions import *

#Apply function to generate adlist data in liverampt format 
primary_industries=['Advertising Services', 'Marketing','Book And Periodical Publishing', 'Entertainment Providers', 'Events Services','Broadcast Media Production And Distribution','Public Relations And Communications Services', 'Online Audio And Video Media', 'Printing Services','Newspaper Publishing', 'Newspapers']
liveramp_adlist_creator(file_path='./raw_data/Adpromoter_FirstPriority.csv', target_industries=primary_industries, adlist_name='secon_priority_liveramp_list')

#events promoter email list
primary_indust=['Events Services', 'Advertising Services']
email_list_creator(file_path='./raw_data/Event-Promoter.csv', target_industries=primary_indust, email_list_name='events_email_list_test')

#check size of the data frmae
get_data("./output_list_database\events_email_list.csv").shape

#merge 1st and second list of liveramp
merge_csv_files("./merger_input_data","./output_list_database/combined_liveramp_list.csv",['Email1','PhoneNumber1'])

#===== email list  part two ================
#read in event_promoter data
events=get_data("./raw_data/Event-Promoter.csv")

# filter for us state
usa_df=filter_usa_states(events)

#filter for email using buiness and personal emails
patial_email_enrich_df=filter_by_valid_business_personal_email(usa_df)

patial_email_enrich_df.shape

#drop rows with missing data
partial_df=drop_rows_with_hyphen(patial_email_enrich_df, "Valid_Business_Email")
f"Total number of rows={partial_df.shape[0]}"





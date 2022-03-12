from requests import get
from Filter_params_set import not_permited_iteration_01, not_permited_iteration_02, main_link_24h, main_link_3d, main_link_7d, post_fix, number_list
from datetime import datetime
import os

# initial const section
output = {}
counter = 0 
message = ''
page_countity = 0
published = 0
Current_iteration_scanned = []
pre_scanned = []

# let's look for already scaned vacancies
file_path = os.path.dirname(__file__) + os.sep + 'pre_scaned.txt'
if os.path.exists(file_path):
    with open(file_path, "r") as text_file:
        for line in text_file:
            pre_scanned.append(line.strip())
        text_file.close()

# optional var section
# you should change scan period and salary by correcting this variables
parse_link = main_link_7d  # also available - main_link_24h; main_link_3d; main_link_7d
min_rec_sallary = 55000  # minimal requared sallary


def number_cleaner(numb_to_clean: str) -> str:
    # cleaning numbers for sallary filters
    out_number = ''
    for chr in numb_to_clean:
        for nmb in number_list:
            if nmb == chr:
                if nmb == '–':
                    nmb = '-'
                out_number = out_number + nmb
    return out_number


def initial_scan(work_link: str) -> int:
    # figuring how much vacancies were published and how many pages it is
    global published, page_countity
    init_page = get(work_link).text
    str_number = init_page[init_page.index('Našli jsme <strong>') + 19 : init_page.index('</strong> nabídek')]
    out_number = number_cleaner(str_number) 
    published = int(out_number)
    if (published / 30) % 1 > 0 :
        page_countity = int(published / 30) + 1
    else:
        page_countity = int(published / 30)


def word_cleaner(word_to_clean: str) -> str:
    # just cleaning unprinted simbols
    cleaned = word_to_clean.replace('\n            ','')
    cleaned = cleaned.replace('   ', '')
    return cleaned


def check_requirements (lnk: str) -> bool: 
    # looking for not  
    global not_permited_iteration_02
    found = False
    page_to_check = get(lnk).text
    for forbidden_text in not_permited_iteration_02:
        if page_to_check.lower().find(forbidden_text) > 0 :
            found = True
            break
    return found


def link_parser (work_link: str):
    # checking for conditions
    global post_fix, message
    for current_page in range(1, page_countity + 1):
        current_parse_link = work_link + post_fix + str(current_page)
        temp_str_set = get(current_parse_link).text.split('<div class="standalone search-list__item"') 

        for record_index in range (1, len(temp_str_set)):
            position_name = ''
            sallary_range= ''
            min_sallary= ''
            position_link= ''
            position_id = ''
            global output, counter, pre_scanned, Current_iteration_scanned

            # getting field's values
            current_record = temp_str_set[record_index]

            if current_record.find('main-info__title__link">') > 0:
                position_name = current_record[current_record.index('main-info__title__link">')+24 : current_record.index('</a></h3>')]        
            
            if (current_record.find('tags__salary--label">') > 0) and (current_record.find('Kč') > 0):
                sallary_range = number_cleaner(current_record[current_record.index('tags__salary--label">') + 23 : current_record.index('Kč')]) # Обязательна проверка наличия данного поля Kč # еще это было обернуто в WordCleaner
                if sallary_range.find('-') > 0 :
                    min_sallary = sallary_range[0 : sallary_range.index('-')]
                else:
                    min_sallary = 'not set'
            else:
                sallary_range = 'not set'
                min_sallary = 'not set'
            
            if current_record.find('main-info__title"><a href="') > 0:
                position_link = current_record[current_record.index('main-info__title"><a href="') + 27 : current_record.index('data-ad-id="')]
            else:
                filtered = True

            if current_record.find('data-position-id="') > 0:
                position_id = current_record[current_record.index('data-position-id="') + 18 : current_record.index('"><div class')]
        
        # filtering Section:
            if min_sallary == 'not set':
                filtered = False
            else:
                if int(min_sallary) >= min_rec_sallary:
                    filtered = False
                else:
                    filtered = True
            if filtered == False:
                for keyword in not_permited_iteration_01:
                    if (position_name.lower().find(keyword) > 0) or (position_name == ''):
                        filtered = True
                        break
            
            if filtered == False and len(position_link) > 3:
                try:
                    if check_requirements(position_link) == False:
                        filtered = False
                    else:
                        filtered = True
                except:
                    print(position_link)
                    filtered = True

            # filtering by iteration 2
            if filtered == False:
                if ('p_id-' + position_id) in pre_scanned:
                    filtered = True


            if filtered == False:
                counter += 1
                curr_rec = [word_cleaner(position_name), 'p_id-' + position_id, sallary_range, min_sallary, word_cleaner(position_link)]
                Current_iteration_scanned.append('p_id-' + str(position_id))
                pre_scanned.append('p_id-' + str(position_id))
                
                output['fnd_'+str(counter)] = curr_rec

    message = f'Total scaned {str(published)} vacancies for this period \nSelected for review {str(counter)} position.'


def printer():
    # console output
    global output, message, done_time, start_time
    print(message)
    print(f'Done in ' + str(done_time - start_time))
    for key, value in output.items():
        print(key, value)
    
    
def prescaned_updater():
    # saving scaned vacancies list
    global file_path, pre_scanned
    with open(file_path, "w") as text_file:
        for list_unit in pre_scanned:
            text_file.write("%s\n" % list_unit)
        text_file.close()


if __name__ == '__main__':
    start_time = datetime.now()
    initial_scan(parse_link)
    link_parser(parse_link)
    done_time = datetime.now()
    printer()
    prescaned_updater()
    print(Current_iteration_scanned)
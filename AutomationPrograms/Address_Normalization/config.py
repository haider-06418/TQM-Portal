# global variables

file_name = "khi_tickets_2022.csv"


''''source file path:'''
fname = f'data/{file_name}'

file_name= file_name.rsplit('.', 1)[0].lower()

'''normalized csv file path:'''
fname_normalized = f'Data/Processed/{file_name}.csv'


'''normalized excel file path:'''
fname_normalized_excel = f'Data/Processed/{file_name}.xlsx'



'''columns to drop: '''
# columns_to_drop = ['Title', 'Created', 'Close Time', 'Queue']
# columns_to_drop = ['Building Name']
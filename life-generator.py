import sys
import tkinter as tk
from tkinter import ttk
import pandas as pd

#------------------------------------------------------FUNCTION DEFINITIONS----------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------

def sortDataFrame(inputDataframe, input_number_to_generate):
    inputDataframe = inputDataframe.sort_values(by='uniq_id', kind='mergesort')
    #sort by number_of_reviews and select the top number_to_generate*10
    inputDataframe = inputDataframe.sort_values(by='number_of_reviews', ascending=False, kind='mergesort').head(input_number_to_generate*10)
    inputDataframe = inputDataframe.sort_values(by='uniq_id', kind='mergesort')
    #Sort by average_review_rating and select the top number_to_generate
    inputDataframe = inputDataframe.sort_values(by='average_review_rating', ascending=False, kind='mergesort').head(input_number_to_generate)

    return inputDataframe

#------------------------------------------------------------------------------------------------------------------------------------------

def displayResultsGrid(frame, inputDataframe, input_number_to_generate, input_item_category):
    #Display the grid
    gridTitle = tk.Label(frame, text="Top" + str(input_number_to_generate) + " items in " + input_item_category)
    gridTitle.pack()
    
    #Create the treeview used to visualize results
    columns = ['uniq_id', 'product_name', 'number_of_reviews', 'average_review_rating']
    tree = ttk.Treeview(frame, columns=columns, show=['headings'])
    tree.pack(side='left', padx=(20,0))

    #Create Scrollbar for treeview
    scrollBar = ttk.Scrollbar(frame, orient='vertical', command = tree.yview)
    scrollBar.pack(side='right')
    tree.configure(xscrollcommand = scrollBar.set)

    #Create column heading 1: uniq_id
    tree.heading(columns[0], text = columns[0])
    tree.column(columns[0], anchor='e', width=200)

    #Create column heading 2: product_name
    tree.heading(columns[1], text = columns[1])
    tree.column(columns[1], anchor='e', width=340)

    #Create column headings 3-4: number_of_reviews and average_review_rating
    for i in columns[2:]:
        tree.heading(i, text = i)
        tree.column(i, anchor='e', width=130)
    
    #Insert rows into the tree from the dataframe
    for index, row in inputDataframe.iterrows():
        tree.insert('', 'end', values=[inputDataframe.loc[index, columns[0]], inputDataframe.loc[index, columns[1]], inputDataframe.loc[index, columns[2]], inputDataframe.loc[index, columns[3]]])

#------------------------------------------------------------------------------------------------------------------------------------------

def formatCsvOutput(inputDataframe, input_number_to_generate, input_item_category, input_item_type):
    #Select only the columns we want to output
    inputDataframe = inputDataframe[['product_name', 'average_review_rating', 'number_of_reviews']]
    #Rename columns to desired output
    inputDataframe = inputDataframe.rename(columns={'product_name': 'output_item_name', 'average_review_rating': 'output_item_rating', 'number_of_reviews': 'output_item_num_reviews'})
    inputDataframe.insert(0, 'input_number_to_generate', input_number_to_generate)
    inputDataframe.insert(0, 'input_item_category', input_item_category)
    inputDataframe.insert(0, 'input_item_type', input_item_type)

    return inputDataframe

#------------------------------------------------------------------------------------------------------------------------------------------

def generateOutputFromGUI(frame, inputDataframe):

    #Disable the generate results button after press
    global generateResultsButton
    generateResultsButton.config(state='disabled')

    #Retrieve input from entry fields
    input_item_type = 'toys'
    input_item_category = selectedCategory.get()
    input_number_to_generate = int(numberToGenerateEntry.get())


    #Select entries that match chosen category
    inputDataframe = inputDataframe[inputDataframe['amazon_category_and_sub_category'] == input_item_category]

    inputDataframe = sortDataFrame(inputDataframe, input_number_to_generate)

    #Create text that csv has been created.
    outputMessage = tk.Label(frame, text='Output saved to output.csv in current directory.')
    outputMessage.pack()

    displayResultsGrid(frame, inputDataframe, input_number_to_generate, input_item_category)

    inputDataframe = formatCsvOutput(inputDataframe, input_number_to_generate, input_item_category, input_item_type)

    inputDataframe.to_csv('output.csv', index=False)

#------------------------------------------------------------------------------------------------------------------------------------------

def generateCsvFromConditionalArg(inputDataframe, input_item_type, input_item_category, input_number_to_generate):
    #Select entries that match chosen category
    inputDataframe = inputDataframe[inputDataframe['amazon_category_and_sub_category'] == input_item_category]

    inputDataframe = sortDataFrame(inputDataframe, input_number_to_generate)
    inputDataframe = formatCsvOutput(inputDataframe, input_number_to_generate, input_item_category, input_item_type)

    inputDataframe.to_csv('output.csv', index=False)

#------------------------------------------------------------------------------------------------------------------------------------------

def createDatabaseFromCsv(inputFile):
    database = pd.read_csv(inputFile, thousands=',')
    for index in database.index:
        #if the category is not empty, truncate it to only main category
        if not isinstance(database.loc[index,'amazon_category_and_sub_category'], float):
            database.loc[index, 'amazon_category_and_sub_category'] = database.loc[index, 'amazon_category_and_sub_category'].split(" >")[0]
        #if the average review rating is not empty, truncate to just the number. Instead of 'number out of 5 stars'.
        if not isinstance(database.loc[index, 'average_review_rating'], float):
            database.loc[index, 'average_review_rating'] = database.loc[index, 'average_review_rating'].split(" ")[0]

    #Convert number_of_reviews and average_review_rating to numeric data type
    database[['number_of_reviews', 'average_review_rating']] = database[['number_of_reviews', 'average_review_rating']].apply(pd.to_numeric)
    
    return database

#------------------------------------------------------------------------------------------------------------------------------------------

class CsvInputs:
    def __init__(self, input_item_type, input_item_category, input_number_to_generate):
        self.input_item_type = input_item_type
        self.input_item_category = input_item_category
        self.input_number_to_generate = input_number_to_generate

def retrieveInputsFromCsv():
    inputdf = pd.read_csv(sys.argv[1])
    inputs = CsvInputs(inputdf['input_item_type'].iloc[0], inputdf['input_item_category'].iloc[0], int(inputdf['input_number_to_generate'].iloc[0]))

    return inputs

#------------------------------------------------------------------------------------------------------------------------------------------

def createGUIWindow():
    window = tk.Tk()
    window.geometry('840x440')
    window.title('Life Generator - Jacob Souther')

    return window

#------------------------------------------------------------------------------------------------------------------------------------------

def createCategorySelect(window, frame, categories):
    global selectedCategory
    selectedCategory = tk.StringVar(window)
    selectedCategory.set(categories[0])
    categoryLabel = tk.Label(frame, text='Choose a Category')
    categorySelection = tk.OptionMenu(frame, selectedCategory, *categories)
    categoryLabel.pack()
    categorySelection.pack()

#------------------------------------------------------------------------------------------------------------------------------------------

def createNumToGenEntry(frame):
    global numberToGenerateEntry
    entryLabel = tk.Label(frame, text='Number to Generate')
    numberToGenerateEntry = tk.Entry(frame)
    entryLabel.pack()
    numberToGenerateEntry.pack()

#---------------------------------------------------------END FUNCTION DEFINITIONS---------------------------------------------------------

def main():
    database = createDatabaseFromCsv('amazon_co-ecommerce_sample.csv')

    #If input.csv is provided.
    if len(sys.argv) == 2:
        inputs = retrieveInputsFromCsv()
        generateCsvFromConditionalArg(database, inputs.input_item_type, inputs.input_item_category, inputs.input_number_to_generate)

        print('Output saved to output.csv in current directory.')

    #If input.csv is not provided, Create GUI.
    elif len(sys.argv) == 1:
        #Create the GUI window
        window = createGUIWindow()

        inputFrame = tk.Frame()
        categoryFrame = tk.Frame(inputFrame)
        numToGenFrame = tk.Frame(inputFrame)
        outputFrame = tk.Frame()

        #Create the category selection section of GUI
        categories = database['amazon_category_and_sub_category'].sort_values().unique() #Create list of alphabetical unique categories
        createCategorySelect(window, categoryFrame, categories)
        categoryFrame.pack(side='left', padx=30, pady=10)

        #Create number to generate entry field
        createNumToGenEntry(numToGenFrame)
        numToGenFrame.pack(side='right', padx=30, pady=10)

        #Create the generate results button
        global generateResultsButton
        generateResultsButton = tk.Button(outputFrame, text='Generate Results', command=(lambda: generateOutputFromGUI(outputFrame, database)))
        generateResultsButton.pack()

        inputFrame.pack(side='top')
        outputFrame.pack()

        window.mainloop()

    #If the incorrect number of arguments is provided.
    else:
        print('Please provide no conditional arguments to open GUI.\nOtherwise provide 1 conditional argument of input.csv')

if __name__ == '__main__':
    main()
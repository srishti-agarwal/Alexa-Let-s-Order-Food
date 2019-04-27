# Alexa-Let-s-Order-Food
Recommendation Engine for Amazon Fine Food

Dataset: https://www.kaggle.com/snap/amazon-fine-food-reviews/data 

Project Video: https://youtu.be/tm_lIqse5gg

Code Details:
1. Libraries required:
   1. pandas
   2. numpy
   3. bottlenose (for accessing Amazon API)
   4. beautiful-soup
   5. graphlab
   6. scikit-learn


Steps to run:
Before executing any of the following commands, ‘Reviews.csv’ files of the  dataset must be present in the ‘data’ directory (download them from the link above).
   1. Create and save models
      1. Run the command:
         $cd src
         $python main.py create
      2. It will create and save all the models in ‘model’ directory. 
         Please note that there should be a directory named 'model' created before running this command.
   
   2. Running the application
      1. Run the command
         $cd src
         $python main.py
      2. The application can be accessed from http://localhost:5000/
         All the functionalities can be accessed from the application

* Code is developed using python 2.7

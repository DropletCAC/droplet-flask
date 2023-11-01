# droplet-flask
## Flask Server Code for Droplet

The more computational back-end work for Droplet was written in Python and tunneled to the Firebase server and mobile app with the `ngrok` platform. The Flask server handles:
  - Detecting leaks by analyzing user data with a Local Outlier Factor algorithm
  - Predicting rain with a custom LSTM model

Droplet is a mobile application that uses a suite of machine-learning technologies to conserve household water usage by

  - Providing real-time usage and cost estimates w/ DropWatch Smart Meter
  - Detecting leaks using machine learning
  - Analyzing and generating personalized tips on how to save water
  - Predicting rain with a custom LSTM model
  - Monitoring rain collection w/ DropStore Smart Sensor

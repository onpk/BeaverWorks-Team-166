# MIT Beaver Works CREATE Challenge Team 166
[Documentation](https://docs.google.com/document/d/1NVmfb9-BZyq1qKGILPp8CuBjvJc1j0bb0a5SEh6AS7A/edit)

Our website has not launched publicly yet, however, you can access our prototype here on this github page.

## Using the Product

First, Install Python 

[Windows](https://www.youtube.com/watch?v=YKSpANU8jPE)
, [Mac](https://www.youtube.com/watch?v=nhv82tvFfkM)

Using github desktop, clone the repository on your machine, or download the code as a zip file.

Next, Using the terminal, navigate to the repository or folder (BeaverWorks-Team-166) and install the project requirements using
```bash
  pip install -r requirements.txt
  ```

Once the project requirements are installed, navigate to the frontEnd folder and run the file titled:
```bash
  index.py
  ```

After that, ctrl + click the link that appears in your terminal that looks like this:
```bash
   * Running on http://127.0.0.1:5000
  ```

If an ImportError occurs after running the index.py file, try running this in the terminal. These commands should hopefully make the code work:
```bash
  pip uninstall black
  pip uninstall click
  pip install black
  pip install click
  ```
A pre-deployment version of the website that is locally running on your machine will appear. The actual website has not been released publicly yet. Think of this local server as the program itself and not a website.

Click on "Dashboard"

Then, Click on "Start Session", and choose a category

Feel free to register as well. In future deployments, your preferences and progress in scenarios will be saved.

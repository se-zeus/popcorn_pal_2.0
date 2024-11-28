### How to run the project? ⚙️

1. Create an account on [TMDB](https://www.themoviedb.org/).

2. Obtain your API key by clicking on the API link in your account settings.

3. Copy or download this repository to your local machine.

4. Create a new conda environment using the command:

    ```bash
    conda create --name YOUR_ENV_NAME python=3.6.13
    ```

5. Activate the conda environment:

    ```bash
    conda activate YOUR_ENV_NAME
    ```

6. Install all required Python packages using:

    ```bash
    pip install -r requirements.txt
    ```

7. Replace `YOUR_API_KEY` in both instances (line no. 15 and 29) within the `static/recommend.js` file and save the changes.

8. Launch your terminal or command prompt from the project directory and execute `main.py` using the command `python main.py`.

9. Access [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your web browser.

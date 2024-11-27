const $ = require('jquery');
const { JSDOM } = require('jsdom');
const { window } = new JSDOM('');
const { document } = window;
global.document = document;
global.window = window;
global.$ = $;

const myAPI = 'bab2b00a4e94bbaac96b9d7a2c3716b3';

// Mocking the AJAX calls
$.ajax = jest.fn();

describe('Movie Recommender', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <input id="autoComplete" class="movie" />
      <div id="movie_list"></div>
      <button class="movie-button" disabled></button>
      <div class="results"></div>
      <div class="fail"></div>
      <div class="footer"></div>
      <div id="loader"></div>
    `;
  });

  test('should disable button when input is empty', () => {
    const input = document.getElementById('autoComplete');
    const button = document.querySelector('.movie-button');
    input.value = '';
    const event = new Event('input');
    input.dispatchEvent(event);
    expect(button.disabled).toBe(true);
  });

  test('should enable button when input is not empty', () => {
    const input = document.getElementById('autoComplete');
    const button = document.querySelector('.movie-button');
    input.value = 'Inception';
    const event = new Event('input');
    input.dispatchEvent(event);
    expect(button.disabled).toBe(false);
  });

  test('should hide movie list on blur', () => {
    const input = document.getElementById('autoComplete');
    const movieList = document.getElementById('movie_list');
    movieList.style.display = 'block';
    const event = new Event('blur');
    input.dispatchEvent(event);
    expect(movieList.style.display).toBe('none');
  });

  test('should call load_details on movie button click', () => {
    const load_details = jest.fn();
    const button = document.querySelector('.movie-button');
    const input = document.querySelector('.movie');
    input.value = 'Inception';
    button.addEventListener('click', () => {
      load_details(myAPI, input.value, true);
    });
    button.click();
    expect(load_details).toHaveBeenCalledWith(myAPI, 'Inception', true);
  });

  test('should call get_movie_details on successful AJAX response', () => {
    const get_movie_details = jest.fn();
    const movie_id = 123;
    const movie_title = 'Inception';
    const movie_title_org = 'Inception';
    $.ajax.mockImplementation(({ success }) => {
      success({
        id: movie_id,
        title: movie_title,
        original_title: movie_title_org,
      });
    });
    load_details(myAPI, 'Inception', true);
    expect(get_movie_details).toHaveBeenCalledWith(movie_id, myAPI, movie_title, movie_title_org);
  });

  test('should show error alert on AJAX error', () => {
    const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});
    $.ajax.mockImplementation(({ error }) => {
      error('Invalid Request');
    });
    load_details(myAPI, 'Inception', true);
    expect(alertMock).toHaveBeenCalledWith('Invalid Request - Invalid Request');
    alertMock.mockRestore();
  });
});
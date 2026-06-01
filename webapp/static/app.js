/* Минимальный фронтенд для webapp-notes.
 *
 * Сейчас единственная задача — фокусировать поле поиска при открытии страницы,
 * чтобы можно было сразу набирать запрос. Дальнейшие улучшения — на усмотрение.
 */

(function () {
  document.addEventListener("DOMContentLoaded", function () {
    var search = document.querySelector(".search__input");
    if (search && !search.value) {
      search.focus();
    }
  });
})();

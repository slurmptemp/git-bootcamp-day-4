# LAB — день 4

Курс: [«Интенсив по погружению в GIT»](https://slurm.io/git-intensive)


## Базовая задача — `01-merge-vs-rebase`

### Стартовое состояние

На ветке `feat/perf-tuning`: вносили правки для подготовки проекта к тестам производительности — увеличивали таймауты, пул соединений, поднимали число воркеров gunicorn, расширяли лимит выдачи поиска, меняли блок поиска в шапке страницы и оптимизировали Dockerfile под нагрузку.

---

На ветке `main`: делали hardening для продакшена — понижение таймаутов и лимитов до консервативных, добавляли welcome-баннер на главной, ужесточали настройка безопасности в Dockerfile (запуск под non-root, явные таймауты gunicorn под short response).

---

Правки в:
- webapp/config.py — секция PerformanceSection;
- webapp/services.py — функция search_notes (логика scoring и лимиты);
- webapp/templates/index.html — блок над списком заметок;
- Dockerfile — CMD запуска gunicorn.

```bash
# git log --oneline --graph --all (на момент окончания подготовки)
* 1cdf369 (HEAD -> main) fix(prod): tighten timeouts, harden Dockerfile, add welcome banner
| * 59555c5 (origin/feat/perf-tuning, feat/perf-tuning) feat(perf): tune timeouts, pools, workers for perf testing
|/  
* 0d250eb (origin/main) Initial commit: webapp-notes starter
```

![Шаги до конфликта](screenshots/01-pre-merge-history.png)

### Путь A — через `merge`

На ветке `experiment/merge`, выбран `hardening` вариант через `VS Code` ( `был добавлен лишний коммит bda8d1c, к заданию не относится, таймаут там по факту не lower, а наоборот.` ).

```bash
# git --no-pager merge feat/perf-tuning
Auto-merging Dockerfile
CONFLICT (content): Merge conflict in Dockerfile
Auto-merging webapp/config.py
CONFLICT (content): Merge conflict in webapp/config.py
Auto-merging webapp/services.py
CONFLICT (content): Merge conflict in webapp/services.py
Auto-merging webapp/templates/index.html
CONFLICT (content): Merge conflict in webapp/templates/index.html
Automatic merge failed; fix conflicts and then commit the result.


# git --no-pager lg          
*   5bf20fd (HEAD -> experiment/merge) Merge branch 'feat/perf-tuning' into experiment/merge
|\  
| * 59555c5 (origin/feat/perf-tuning, feat/perf-tuning) feat(perf): tune timeouts, pools, workers for perf testing
* | bda8d1c feat(config): lower request timeout
* | 1cdf369 (origin/main, main) fix(prod): tighten timeouts, harden Dockerfile, add welcome banner
|/  
* 0d250eb Initial commit: webapp-notes starter

```

![Состояние Merge Editor / CLI на момент конфликта](screenshots/02-merge-conflict.png)

![Финальный merge-коммит](screenshots/03-merge-result.png)

### Путь B — через `rebase`

На ветке `experiment/rebase` , также выбран `hardening` вариант через `VS Code` ( но `REQUEST_TIMEOUT_SEC` установлен в 7 ).

```bash
# git rebase main
Auto-merging Dockerfile
CONFLICT (content): Merge conflict in Dockerfile
Auto-merging webapp/config.py
CONFLICT (content): Merge conflict in webapp/config.py
Auto-merging webapp/services.py
CONFLICT (content): Merge conflict in webapp/services.py
Auto-merging webapp/templates/index.html
CONFLICT (content): Merge conflict in webapp/templates/index.html
error: could not apply 59555c5... feat(perf): tune timeouts, pools, workers for perf testing
hint: Resolve all conflicts manually, mark them as resolved with
hint: "git add/rm <conflicted_files>", then run "git rebase --continue".
hint: You can instead skip this commit: run "git rebase --skip".
hint: To abort and get back to the state before "git rebase", run "git rebase --abort".
Could not apply 59555c5... feat(perf): tune timeouts, pools, workers for perf testing


# git --no-pager lg
* bbc31c4 (origin/experiment/rebase, experiment/rebase) feat(perf): tune timeouts, pools, workers for perf testing
| *   5bf20fd (HEAD -> experiment/merge, origin/experiment/merge) Merge branch 'feat/perf-tuning' into experiment/merge
| |\  
| | * 59555c5 (origin/feat/perf-tuning, feat/perf-tuning) feat(perf): tune timeouts, pools, workers for perf testing
| * | bda8d1c feat(config): lower request timeout
|/ /  
* / 1cdf369 (origin/main, main) fix(prod): tighten timeouts, harden Dockerfile, add welcome banner
|/  
* 0d250eb Initial commit: webapp-notes starter
```

![История после rebase](screenshots/04-rebase-result.png)

### Сравнение

Финальная история всех веток рядом:

![Сравнение историй experiment/merge vs experiment/rebase](screenshots/05-history-comparison.png)

В процессе сравнения (например):

|Ветка|Историия|Хэши Коммитов|Видимость Ветки в истории|
|-|-|-|-|
|**experiment/merge**|С ветвлением. N-commits+merge-commit|не меняются|V|
|**experiment/rebase**|Линейная. N-commits|меняются|X|

### Какой подход я бы выбрал(а) в команде и почему

`Merge`  - например, для `Merge Request` в `master`/`main`, командная работа, явная видимость того что правки велись в отдельной ветке.
`Rebase` - локальная работа в своей ветке, чтобы "подтянуть убежавшие вперед" коммиты, сохранения линейности истории.

В примере c `merge` мы получили нелинейную историю
```bash
# git --no-pager log --decorate --oneline --graph experiment/merge 
*   5bf20fd (HEAD -> experiment/merge, origin/experiment/merge) Merge branch 'feat/perf-tuning' into experiment/merge
|\  
| * 59555c5 (origin/feat/perf-tuning, feat/perf-tuning) feat(perf): tune timeouts, pools, workers for perf testing
* | bda8d1c feat(config): lower request timeout
* | 1cdf369 (origin/main, main) fix(prod): tighten timeouts, harden Dockerfile, add welcome banner
|/  
* 0d250eb Initial commit: webapp-notes starter
```
с `rebase` наоборот
```bash
# git --no-pager log --decorate --oneline --graph experiment/rebase
* bbc31c4 (origin/experiment/rebase, experiment/rebase) feat(perf): tune timeouts, pools, workers for perf testing
* 1cdf369 (origin/main, main) fix(prod): tighten timeouts, harden Dockerfile, add welcome banner
* 0d250eb Initial commit: webapp-notes starter
```
`rebase` не содержит "лишнего" merge-коммит.
```bash
# git --no-pager log --merges --oneline experiment/rebase
#
```
`merge` наоборот
```
# git --no-pager log --merges --oneline experiment/merge 
5bf20fd (HEAD -> experiment/merge, origin/experiment/merge) Merge branch 'feat/perf-tuning' into experiment/merge
```

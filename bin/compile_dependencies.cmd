@echo off

for /F "tokens=1" %%i in ('git rev-parse --show-toplevel') do set toplevel=%%i

cd %toplevel%

REM Base deps
pip-compile^
    --no-emit-index-url^
    requirements/base.in

REM Production deps
pip-compile^
    --no-emit-index-url^
    --output-file requirements/production.txt^
    requirements/base.txt^
    requirements/production.in

REM CI deps
pip-compile^
    --no-emit-index-url^
    --output-file requirements/ci.txt^
    requirements/base.txt^
    requirements/testing.in^
    requirements/ci.in

REM Dev deps
pip-compile^
    --no-emit-index-url^
    --output-file requirements/dev.txt^
    requirements/base.txt^
    requirements/testing.in^
    requirements/dev.in

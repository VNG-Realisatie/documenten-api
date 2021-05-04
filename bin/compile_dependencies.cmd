@echo off

for /F "tokens=1" %%i in ('git rev-parse --show-toplevel') do set toplevel=%%i

cd %toplevel%

REM Base deps
pip-compile^
    --no-emit-index-url^
    requirements/base.in

REM Jenkins/tests deps
pip-compile^
    --no-emit-index-url^
    --output-file requirements/jenkins.txt^
    requirements/base.txt^
    requirements/testing.in^
    requirements/jenkins.in

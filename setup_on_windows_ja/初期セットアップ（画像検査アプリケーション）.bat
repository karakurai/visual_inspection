@echo off

rem Python�̃o�[�W�������m�F����
echo Python�̃o�[�W�������m�F���܂��B
python --version 2>NUL

rem �G���[���x�����`�F�b�N���ď����𕪊�
if errorlevel 1 (
    rem Python���C���X�g�[������Ă��Ȃ��ꍇ
    echo ------------------------------------------------------------
    echo Python3.9���C���X�g�[�����Ă��������B
    echo ------------------------------------------------------------
    pause
    exit
) else (
    rem Python���C���X�g�[������Ă���ꍇ
    for /f "tokens=2" %%A in ('python --version 2^>^&1') do (
        set "python_version=%%A"
    )
    
    rem �o�[�W������3.9�n���ǂ������`�F�b�N
    echo %python_version% | findstr /r "^3\.9\..*"
    if %errorlevel% == 0 (
        echo Python3.9���C���X�g�[������Ă��܂��B�Z�b�g�A�b�v���J�n���܂��B
    ) else (
        echo ------------------------------------------------------------
        echo Python�̃o�[�W�������Ⴂ�܂��BPython3.9���C���X�g�[�����Ă��������B
        echo ------------------------------------------------------------
        pause
        exit
    )
)

rem �W�J����ZIP�t�@�C�����w��
set zipFilePath=visual_inspection-main.zip

rem �W�J��t�H���_���w��
set destFolderPath=.\

rem ���s����PowerShell�̃R�}���h���b�g��g�ݗ���
set psCommand=powershell -NoProfile -ExecutionPolicy Unrestricted Expand-Archive -Path %zipFilePath% -DestinationPath %destFolderPath% -Force

rem PowerShell�œW�J�����s
echo ZIP�t�@�C����W�J��...
%psCommand%

rem �W�J���ʂ��m�F
if %errorlevel% == 0 (
    echo %zipFilePath% �t�@�C����W�J���܂����B
) else (
    echo ------------------------------------------------------------
    echo %zipFilePath% �t�@�C���̓W�J�Ɏ��s���܂����B
    echo ------------------------------------------------------------
    pause
    exit
)

cd .\visual_inspection-main

rem Python�̉��z�����쐬
echo Python���z�����쐬��...
python -m venv .inspection_app

rem Python�̉��z�����N��
call ".\.inspection_app\Scripts\activate.bat"

rem pip���A�b�v�O���[�h
echo pip���A�b�v�O���[�h��...
python -m pip install --upgrade pip

rem ���C�u�������C���X�g�[��
echo Python���C�u�������C���X�g�[����...
pip install -r requirements.txt

echo ------------------------------------------------------------
echo �摜�����A�v���P�[�V�����̏����Z�b�g�A�b�v�����튮�����܂����B
echo ------------------------------------------------------------

pause
exit
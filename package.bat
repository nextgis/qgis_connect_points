mkdir connect_points
mkdir connect_points\icons
mkdir connect_points\i18n
xcopy *.py connect_points
xcopy *.ui connect_points
xcopy README.md connect_points
xcopy LICENSE connect_points
xcopy metadata.txt connect_points
xcopy icons\connect_points.svg connect_points\icons\connect_points.svg
xcopy icons\settings.svg connect_points\icons\settings.svg
xcopy i18n\connect_points_ru.ts connect_points\i18n\connect_points_ru.ts
lrelease connect_points\i18n\connect_points_ru.ts
del connect_points\i18n\connect_points_ru.ts
zip -r connect_points.zip connect_points
del /s /q connect_points
rmdir /s /q connect_points
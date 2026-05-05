Что лежит в /tmp от моего пользователя (info-only, без удаления):
!`{
  ME=$(whoami)
  echo "── мои файлы /tmp (top 20 по размеру) ──"
  find /tmp -maxdepth 3 -user "$ME" -type f -printf '%s\t%p\n' 2>/dev/null | sort -rn | head -20 | awk '{printf "%6.1f MB  %s\n", $1/1024/1024, $2}'
  echo ""
  echo "── мои директории /tmp (с размером) ──"
  find /tmp -maxdepth 2 -user "$ME" -type d 2>/dev/null | xargs -I{} du -sh {} 2>/dev/null | sort -hr | head -10
  echo ""
  echo "Удалить ничего не удалено. Чтобы почистить — запусти явно:"
  echo "  find /tmp -maxdepth 3 -user $ME -mtime +3 -delete"
}`

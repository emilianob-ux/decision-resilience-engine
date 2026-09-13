# Contribuir

Este es un repo de portfolio mantenido por una sola persona. **No busco
contribuciones de código de gran alcance** y es honesto decirlo en vez de simular una
comunidad: una PR grande y no acordada probablemente quede sin mergear.

Lo que sí es muy bienvenido, en orden de valor:

1. **Desafiar un claim.** Si el README, el `AUDIT.md` o cualquier doc afirma algo que
   el código no respalda, abrí un issue con la plantilla *"Un claim no se sostiene"*.
   Es la contribución que más valoro: el repo entero existe para argumentar que un
   sistema debe poder demostrar lo que dice.
2. **Reportar que algo no corre.** Sobre todo el quickstart o la demo, en un sistema
   operativo o versión de Python donde no los probé.
3. **Discutir diseño.** Especialmente los P1/P2 pendientes del [AUDIT.md](AUDIT.md).
   Comentá en un issue antes de escribir código.

## Si vas a mandar una PR

Que pase lo mismo que corre CI:

```bash
pip install -r requirements.txt -r requirements-dev.txt
ruff check . && ruff format --check .    # ruff está pineado exacto a propósito
pytest tests/ -q
bash scripts/demo_dre.sh
```

Convenciones del repo:

- **Las invariantes se testean.** Si tu cambio toca gobernanza, FSM o checkpoints,
  agregá el test en `tests/test_dre_invariants.py`, no un smoke.
- **Si cambiás `dre/contracts/`, actualizá el snippet del ICD** en
  `docs/pdr/02_Interface_Contracts_ICD.md`: hay un test que verifica que sean copia
  literal y va a fallar.
- **No infles el alcance en la documentación.** Si algo es un proxy, el doc dice
  *proxy*. Ver `docs/DRE_IMPLEMENTATION_STATUS.md`.
- Commits en español o inglés, agrupados por intención.

## Seguridad

Vulnerabilidades: no abras un issue público. Ver [SECURITY.md](SECURITY.md).

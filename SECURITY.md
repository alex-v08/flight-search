# Seguridad y Privacidad

## 🔒 Información Sensible

Este proyecto NO incluye en el repositorio:

### ❌ NO Incluido (Protegido por .gitignore)
- API Keys (`.env`)
- Rutas de usuario específicas
- IPs o hostnames personales
- Datos de sesión
- Historial de precios personal
- Logs del sistema

### ✅ Incluido (Público y Seguro)
- Código fuente
- Documentación genérica
- Ejemplos de configuración (`.env.example`)
- Scripts de instalación

## 🛡️ Protección de Datos

### API Keys
- **Brave Search API**: Configurada en `.env` (ignorado por git)
- **Ollama**: Local, sin API keys necesarias
- Nunca commitear `.env` al repositorio

### Rutas del Sistema
- Todas las rutas específicas han sido reemplazadas por variables genéricas
- Usar `$SCRIPT_DIR` en scripts
- Usar paths relativos cuando sea posible

### Variables de Usuario
- Reemplazar `/home/username` con `/home/$USER` o rutas relativas
- Usar variables de entorno para paths personalizados

## 🔐 Antes de Hacer Push

### Verificar que NO se incluya:

```bash
# Verificar archivos staged
git status

# Verificar contenido de archivos
git diff --cached

# Buscar datos sensibles
git grep -i "api.*key\|password\|secret"
git grep "/home/[a-z]"
```

### Limpiar Historial (si se commiteó algo sensible)

```bash
# CUIDADO: Esto reescribe el historial
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# Forzar push (solo si es necesario)
git push origin --force --all
```

## 📋 Checklist Pre-Commit

- [ ] `.env` está en `.gitignore`
- [ ] No hay API keys en el código
- [ ] Rutas son genéricas o relativas
- [ ] No hay nombres de usuario específicos
- [ ] No hay IPs privadas
- [ ] `.env.example` usa placeholders
- [ ] Logs están ignorados

## 🔍 Datos Reemplazados

### En este proyecto se reemplazó:

| Original | Reemplazado por |
|----------|-----------------|
| `/home/alexv/...` | `/path/to/...` o `$SCRIPT_DIR` |
| `pop-os` | `your-hostname` o `$HOSTNAME` |
| API Key específica | `your_api_key_here` |
| Usuario específico | `$USER` o genérico |

## 🚨 Si Encuentras Datos Sensibles

1. **Reporta** un issue privado
2. **No expongas** los datos encontrados públicamente
3. **Propón** un pull request con la corrección
4. Usa variables genéricas en su lugar

## 📖 Mejores Prácticas

### Al Configurar

```bash
# Copiar ejemplo
cp .env.example .env

# Editar con tus datos (NUNCA commitear)
nano .env

# Verificar que está ignorado
git check-ignore .env
```

### Al Desarrollar

```python
# MAL: Hardcodear paths
path = "/home/alexv/project"

# BIEN: Usar paths relativos
import os
path = os.path.dirname(os.path.abspath(__file__))

# BIEN: Usar variables de entorno
path = os.getenv("PROJECT_PATH", ".")
```

### Al Documentar

```markdown
# MAL: Rutas específicas
cd /home/alexv/workspace/flight-search

# BIEN: Rutas genéricas
cd /path/to/flight-search

# MEJOR: Usar variables
cd $PROJECT_DIR
```

## 🔑 Obtener API Keys de Forma Segura

### Brave Search API
1. Visita: https://brave.com/search/api/
2. Registra una cuenta
3. Obtén tu API key
4. Guárdala en `.env` (nunca en código)

### Ollama
- No requiere API key
- Corre 100% local
- Sin datos enviados a internet

## 📞 Contacto de Seguridad

Si encuentras vulnerabilidades de seguridad:
- **NO** abras un issue público
- Contacta directamente al mantenedor
- Usa GitHub Security Advisory si está disponible

---

**Recuerda**: La seguridad es responsabilidad de todos. Revisa siempre antes de hacer push!

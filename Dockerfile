FROM odoo:18.0

# Instalar dependencias adicionales
USER root
RUN apt-get update && apt-get install -y \
    python3-pip \
    && pip3 install -r /requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER odoo

# Copiar archivos de configuración y módulos
COPY ./config/odoo.conf /etc/odoo.conf
COPY ./addons /mnt/extra-addons

# Establecer el directorio de trabajo
WORKDIR /mnt/extra-addons

# Exponer el puerto de Odoo
EXPOSE 8069

# Comando para iniciar Odoo
CMD ["odoo", "-c", "/etc/odoo.conf"]
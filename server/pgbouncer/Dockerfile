FROM pgbouncer/pgbouncer:latest

# Install additional tools for debugging
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration files
COPY pgbouncer.ini /etc/pgbouncer/
COPY userlist.txt /etc/pgbouncer/

# Create directory for logs
RUN mkdir -p /var/log/pgbouncer

# Expose PgBouncer port
EXPOSE 6432

# Start PgBouncer with proper user
CMD ["pgbouncer", "-u", "postgres", "/etc/pgbouncer/pgbouncer.ini"]

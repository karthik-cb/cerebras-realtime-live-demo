FROM pgbouncer/pgbouncer:latest

# Install additional tools for debugging (Alpine Linux uses apk)
RUN apk add --no-cache postgresql-client

# Copy configuration files
COPY pgbouncer.ini /etc/pgbouncer/
COPY userlist.txt /etc/pgbouncer/

# Create directory for logs
RUN mkdir -p /var/log/pgbouncer

# Expose PgBouncer port
EXPOSE 6432

# Start PgBouncer with proper user
CMD ["pgbouncer", "-u", "postgres", "/etc/pgbouncer/pgbouncer.ini"]

FROM debian:latest

RUN apt update && apt install openssh-server xfce4-terminal sudo nano python3 git curl -y

WORKDIR /etc/ssh

COPY sshd_config ./

RUN useradd -rm -s /bin/bash -g root -G sudo -u 1000 boundaries 

WORKDIR /home/boundaries

RUN su boundaries -l -c "curl https://raw.githubusercontent.com/pauljako/boundaries/main/install.py | python3"

RUN su boundaries -l -c "echo "PATH=/home/boundaries/boundaries/exec/bin:$PATH" >> /home/boundaries/.profile"

RUN su boundaries -l -c "ln -s /home/boundaries/boundaries/apps/boundaries/main.py /home/boundaries/boundaries/exec/bin/boundaries"

RUN su boundaries -l -c "git clone https://github.com/pauljako/bnd-repo.git"

RUN su boundaries -l -c "python3 /home/boundaries/boundaries/apps/boundaries/main.py install bnd-repo"

COPY index.json ./boundaries/var/bnd-repo/repos/

RUN su boundaries -l -c "python3 /home/boundaries/boundaries/apps/boundaries/main.py run bnd-repo update"

RUN su boundaries -l -c "rm -rf bnd-repo"

RUN echo "boundaries:boundaries" | chpasswd

RUN service ssh start

EXPOSE 22

CMD ["/usr/sbin/sshd","-D"]

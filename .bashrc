# Enable tab completion
source ~/git-completion.bash

# colors!
green="\[\033[0;32m\]"
blue="\[\033[0;34m\]"
lightBlue="\e[94m"
purple="\[\033[0;35m\]"
reset="\[\033[0m\]"

# Change command prompt
source ~/git-prompt.sh
export GIT_PS1_SHOWDIRTYSTATE=1
# '\u' adds the name of the current user to the prompt
# '\$(__git_ps1)' adds git-related stuff
# '\W' adds the name of the current directory
export PS1="$blue\W$green\$(__git_ps1) $ $reset"

export NODE_PATH=$NODE_PATH:/home/YOUR_ROUTE/.npm-global/lib/node_modules

#Personal alias
alias install="sudo apt-get install"
alias poweroff="sudo shutdown -h now"
alias cl="cdl"
alias cll="cdll"
alias ll="ls -l"
alias lh="ls -lah"
alias md="mcdf"
alias lll="ll | lolcat"
alias lhl="lh | lolcat"
alias ..="cd .."
alias .="cd"
alias clip="xclip -i -selection c"
alias plip="xclip -o -selection c"
alias hf="hideFile"
alias bk="bkf"
alias servers="cat /etc/nginx/sites-enabled/default"
alias games-list="cat ~/.bsdgames"
alias ports="netstat -tulanp"

#Start openvpn
startVPN() { cd /etc/openvpn; sudo openvpn --config /etc/openvpn/YOUR_CONFIG.conf;}
alias vpnOn="startVPN"
alias vpnStart="/etc/init.d/openvpn start"
alias vpnStop="/etc/init.d/openvpn stop"

#Make folder and cd into it
mcdf() { mkdir -p "$1"; cd "$1";} 

#Go folder and list its content
cdl() { cd "$1"; ll;}
cdll() { cd "$1"; ll | lolcat;}

#Bakcup a file
bkf() { cp "$1"{,.bak};}

#Hide file
hideFile() {
	if [[ $# == 1 ]]; then
      if [ ! -f $@ ]; then
      	echo "File not found!"
      else
      	mv $@ .$@
      fi
    else
        echo "Hide one file at time"
    fi
}

#Change personal account
gitToPersonal() {
	#remove ssh cache
	ssh-add -D
	#add ssh 
	ssh-add ~/.ssh/id_personal
	#change git config mail
	git config --global user.email YOUR_MAIL
}

alias gtp="gitToPersonal"

#Install nInvaders & BSDGames
installGames() {
	install ninvaders
	install bsdgames
}

#Install themes
installThemes() {
	echo -e "create \e[94mThemes \e[39mfolder"
	mkdir ~/Themes
	echo -e "go to \e[94mThemes \e[39mfolder"
	cd ~/Themes
	echo -e "clone repository \e[94mthemes-icons-pack"
	git clone https://github.com/erikdubois/themes-icons-pack.git
	echo -e "go to \e[94mthemes-icons-pack \e[39mfolder"
	cd themes-icons-pack
	echo -e "installing \e[94mthemes"
	./all-in-once-installation_deb_themes.sh
	echo -e "installing \e[94micons"
	./all-in-once-installation_deb_icons.sh
}

#Install conky
installConky() {
	echo -e "create \e[94mThemes/Conky \e[39mfolder"
	mkdir ~/Themes/Conky
	echo -e "go to \e[94mConky \e[39mfolder"
	cd ~/Themes/Conky
	echo -e "clone repository \e[94mAureola"
	git clone https://github.com/erikdubois/Aureola
	echo -e "go to \e[94mAureola\e[39mfolder"
	cd Aureola
	./get-aureola-from-github-to-local-drive.sh
	cd ~/.aureola
	./get-aureola-from-github-to-local-drive.sh
	# ./install-conky.sh
	echo -e "go to folder and execute \e[94m./install-conky.sh"
}

#Git alias
g() {
    if [[ $# > 0 ]]; then
      git $@
    else
        git status -sb
    fi
}

#Kubernetes 

LASTKUBE=""

kubepre() {
    if [ "$LASTKUBE" != "pre" ]; then
        LASTKUBE="pre"
        gcloud container clusters get-credentials PRE_CLUSTER --zone europe-west1-b
    fi
}

kubectlpre() {
    kubepre
    kubectl "$@"
}

kubeint() {
    if [ "$LASTKUBE" != "int" ]; then
        LASTKUBE="int"
        gcloud container clusters get-credentials INT_CLUSTER --zone europe-west1-c
    fi
}

kubectlint() {
    kubeint
    kubectl "$@"
}

kubepro() {
    if [ "$LASTKUBE" != "pro" ]; then
        LASTKUBE="pro"
        gcloud container clusters get-credentials PRO_CLUSTER --zone europe-west1-d
    fi
}

kubectlpro() {
    kubepro
    kubectl "$@"
    echo "you are in pro cluster! Be careful!"
}

#Alias kubernetes
alias kbcl="kubectl"
alias kbclpre=kubectlpre
alias kbclint=kubectlint
alias kbclpro=kubectlpro

alias kubewhere="kubectl config current-context"

alias prepods="kubectlpre get pods -o wide"
alias intpods="kubectlint get pods -o wide"
alias propods="kubectlpro get pods -o wide"

alias preserv="kubectlpre get service"
alias intserv="kubectlint get service"
alias proserv="kubectlpro get service"

alias pretop='kubectlpre top pod | sed  's/Mi//' | tail -n +2 | sort -n -k 3 -r'
alias inttop='kubectlint top pod | sed  's/Mi//' | tail -n +2 | sort -n -k 3 -r'
alias protop='kubectlpro top pod | sed  's/Mi//' | tail -n +2 | sort -n -k 3 -r'

alias prelogs='kubectlpre logs -f'
alias intlogs='kubectlint logs -f'
alias prologs='kubectlpro logs -f'

alias poddes='kubectl describe pod'
alias servdes='kubectl describe service'

kubepreexec() {
    kubectlpre exec -i "$@" -- /bin/sh
}

kubeintexec() {
    kubectlint exec -i "$@" -- /bin/sh
}

kubeproexec() {
    kubectlpro exec -i "$@" -- /bin/sh
}
alias infoNewDeploy="cat ~/.deploy-new-proyect.txt"
alias infoDeployPre="cat ~/.deploy-pre.txt"
alias infoDeployPro="cat ~/.deploy-pro.txt"

# tabtab source for yo package
# uninstall by removing these lines or running `tabtab uninstall yo`
[ -f /home/YOUR_ROUTE/.npm-global/lib/node_modules/yo/node_modules/tabtab/.completions/yo.bash ] && . /home/YOUR_ROUTE/.npm-global/lib/node_modules/yo/node_modules/tabtab/.completions/yo.bash  

# The next line updates PATH for the Google Cloud SDK.
if [ -f /opt/google-cloud-sdk/path.bash.inc ]; then
  source '/opt/google-cloud-sdk/path.bash.inc'
fi

# The next line enables shell command completion for gcloud.
if [ -f /opt/google-cloud-sdk/completion.bash.inc ]; then
  source '/opt/google-cloud-sdk/completion.bash.inc'
fi

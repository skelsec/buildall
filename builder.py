from git import Repo, Git
import pathlib
import datetime
import platform
import venv
import os
import stat

# LocalNTLMTest

PORCHETTA_TOOLS = {
    'aiowinreg'    : ('main', 'Porchetta-Industries', 'python'),
    'aesedb'       : ('main', 'Porchetta-Industries', 'python'),
    'kerberoast'   : ('main', 'Porchetta-Industries', 'python'),
    'unicrypto'    : ('main', 'Porchetta-Industries', 'python'),
    'asyauth'      : ('main', 'Porchetta-Industries', 'python'),
    'winacl'       : ('main', 'Porchetta-Industries', 'python'),
    'minidump'     : ('main', 'Porchetta-Industries', 'python'),
    'amurex'       : ('main', 'Porchetta-Industries', 'python'),
    'aardwolfgui'  : ('main', 'Porchetta-Industries', 'python'),
    'minikerberos' : ('main', 'Porchetta-Industries', 'python'),
    'aiosmb'       : ('main', 'Porchetta-Industries', 'python'),
    'msldap'       : ('main', 'Porchetta-Industries', 'python'),
    'aardwolf'     : ('main', 'Porchetta-Industries', 'python'),
    'pypykatz'     : ('main', 'Porchetta-Industries', 'python'),
    'pysnaffler'   : ('main', 'Porchetta-Industries', 'python'),
    'evilrdp'      : ('main', 'Porchetta-Industries', 'python'),
    'ofscandecrypt': ('main', 'Porchetta-Industries', 'python'),
    'asysocks'     : ('main', 'Porchetta-Industries', 'python'),
    'flatkatz'     : ('main', 'Porchetta-Industries', 'python'),
    'winsspi'      : ('main', 'Porchetta-Industries', 'python'),
    'wsnet'        : ('main', 'Porchetta-Industries', 'python'),
    'zipserver'    : ('main', 'Porchetta-Industries', '.net'),
    'wsnet-dotnet' : ('main', 'Skelsec', '.net'),
    'wsnet-nim'    : ('main', 'Skelsec', 'nim'),
    'octopwn'      : ('main', 'Skelsec', 'python'),
    'octopwnpage'  : ('main', 'Skelsec', 'python'),
    'antlmrelay'   : ('main', 'Skelsec', 'python'),
    'jackdaw'      : ('main', 'Skelsec', 'python'),
}

INSTALL_ORDER = {
    'unicrypto' : None,
    'asysocks' : None,
    'winacl' : None,
    'minikerberos' : None,
    'asyauth' : None,
    'kerberoast' : None,
    'wsnet' : None,
    'aiowinreg' : None,
    'aesedb' : None,
    'minidump' : None,
    'amurex' : None,
    'aiosmb' : None,
    'msldap' : None,
    'aardwolf' : None,
    'aardwolfgui' : None,
    'evilrdp' : None,
    'ofscandecrypt' : None,
    'pypykatz' : None,
    'pysnaffler' : None,
    'octopwn' : None,
}



def create_install_batch(venv_path:pathlib.Path, repo_path:pathlib.Path, wheeldir, install_order):
    results_path = repo_path.parent.joinpath('results')
    install_lines = []
    builder_lines = ['@echo off', 'set __BUILDALL_VENV__=1', 'pip install pyinstaller']
    activate_path = venv_path.joinpath('Scripts', 'activate.bat').absolute()
    install_lines.append(str(activate_path))
    
    for packagename in install_order:
        package_path = repo_path.joinpath(packagename).absolute()
        install_lines.append(f'cd {package_path} && pip install . && pip wheel . -w {wheeldir} --no-deps')
        if install_order[packagename] is not None:
            presdir = results_path.joinpath(packagename).absolute()
            presdir.mkdir(parents=True, exist_ok=False)
            builder_lines.append(f'cd {install_order[packagename]}')
            builder_lines.append('CALL build.bat')
            builder_lines.append(f'copy *.exe {presdir}')
    
    builder_lines.append(f'cd {repo_path.parent.absolute()}')
    install_text = '@echo off\r\n'+' &^\r\n'.join(install_lines) + f'\r\ncd {repo_path.parent.absolute()}'
    builder_text = '\r\n'.join(builder_lines)

    installpath = None
    builderpath = None
    if install_text is not None:
        installpath = repo_path.parent.joinpath('install.bat').absolute()
        with open(installpath, 'w', newline = '') as f:
            f.write(install_text)
    
    if builder_text is not None:
        builderpath = repo_path.parent.joinpath('build.bat').absolute()
        with open(builderpath, 'w', newline='') as f:
            f.write(builder_text)

    return installpath, builderpath

def create_install_linux(venv_path:pathlib.Path, repo_path:pathlib.Path, wheeldir, install_order):
    activate_path = venv_path.joinpath('bin', 'activate').absolute()
    install_lines = ['#!/bin/bash']
    install_lines.append('source ' + str(activate_path))
    for packagename in install_order:
        package_path = repo_path.joinpath(packagename).absolute()
        install_lines.append(f'cd {package_path} && pip install . && pip wheel . -w {wheeldir} --no-deps')
    
    install_text = '\n'.join(install_lines)
    installpath = None
    if install_text is not None:
        installpath = repo_path.parent.joinpath('install.sh').absolute()
        with open(installpath, 'w', newline = '') as f:
            f.write(install_text)
        fstat = os.stat(installpath)
        os.chmod(installpath, fstat.st_mode | stat.S_IEXEC)
    
    return installpath, None

def clone_github_repo(name, dstdir, branch = 'main'):
    repo = Repo.clone_from(
        f'https://github.com/skelsec/{name}',
        str(dstdir),
        branch=branch
    )

def clone_porchetta_repo(projectname, reponame, dstdir, ssh_cmd, branch = 'main'):
    Repo.clone_from(
        f'git@ssh.git.porchetta.industries:{reponame}/{projectname}',
        str(dstdir),
        branch=branch,
        env={'GIT_SSH_COMMAND': ssh_cmd}
    )

def check_pyinstaller(reponame, dstfolder:pathlib.Path, install_order):
    builderdir = dstfolder.joinpath('builder','pyinstaller')
    builderpath = dstfolder.joinpath('builder','pyinstaller', 'build.bat')
    if builderpath.exists() is False:
        print('\t\tRepo %s doesn\'t have a pyinstaller script!' % reponame)
        return False
    
    with open(builderpath, 'r') as f:
        filedata = f.read()
        allok = True
        if filedata.find('__BUILDALL_VENV__') == -1:
            print('\t\t\tRepo %s doesn\'t have up-to-date builder!' % reponame)
            allok = False
        if filedata.find(':CREATEVENV') == -1:
            print('\t\t\tRepo %s doesn\'t build env aware builder!' % reponame)
            allok = False
        if allok is True:
            install_order[reponame] = builderdir.absolute()
    return True

def check_pyproject(reponame, dstfolder:pathlib.Path):
    # has pyproject
    checkpath = dstfolder.joinpath('pyproject.toml')
    if checkpath.exists() is False:
        print('\t\tRepo %s doesn\'t have pyproject.toml file!' % reponame)
        return False
    return True

def check_license(reponame, dstfolder:pathlib.Path):
    checkpath = dstfolder.joinpath('LICENSE')
    if checkpath.exists() is False:
        print('\t\tRepo %s doesn\'t have LICENSE file!' % reponame)
        return False
    return True

def check_manifest(reponame, dstfolder:pathlib.Path):
    checkpath = dstfolder.joinpath('MANIFEST.in')
    if checkpath.exists() is False:
        print('\t\tRepo %s doesn\'t have MANIFEST.in file!' % reponame)
        return False
    return True

def check_version(reponame, dstfolder:pathlib.Path):
    checkpath = dstfolder.joinpath(reponame, '_version.py')
    if checkpath.exists() is False:
        print('\t\tRepo %s doesn\'t have _version.py file!' % reponame)
        return False
    return True


def prepare_env_and_fetch_projects(basedir:pathlib.Path, ssh_cmd:str, steps:int = 4):
    builddir = basedir.joinpath('build_'+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")).absolute()
    builddir.mkdir()
    wheeldir = builddir.joinpath('wheels')
    wheeldir.mkdir()
    print('BUILD DIR: %s' % builddir)
    print('WHEEL DIR: %s' % wheeldir)
    #print('Fetching repos from Github...')
    #for reponame in GITHUB_TOOLS:
    #    dstfolder = builddir.joinpath('repos', reponame).absolute()
    #    print('\tCloning %s to %s' % (reponame, dstfolder))
    #    clone_github_repo(reponame, dstfolder, branch = GITHUB_TOOLS[reponame])
    #    check_pyinstaller(reponame, dstfolder, INSTALL_ORDER)
    #    check_license(reponame, dstfolder)
    #    check_manifest(reponame, dstfolder)
    #    check_version(reponame, dstfolder)
    #    check_pyproject(reponame, dstfolder)
    
    print('Fetching repos from Porchetta Industries')
    for projectname in PORCHETTA_TOOLS:
        branchname, repouser, lang = PORCHETTA_TOOLS[projectname]
        dstfolder = builddir.joinpath('repos', projectname).absolute()
        print('\tCloning %s to %s' % (projectname, dstfolder))
        clone_porchetta_repo(projectname, repouser, dstfolder, ssh_cmd, branch = branchname)
        if lang.lower() == 'python':
            check_pyinstaller(projectname, dstfolder, INSTALL_ORDER)
            check_license(projectname, dstfolder)
            check_version(projectname, dstfolder)
            check_pyproject(projectname, dstfolder)
            check_manifest(projectname, dstfolder)
        else:
            print('Not a python project, skipping checks')

    if steps <= 1:
        return None, None
    
    print('Creating virtual environment...')
    envdir = builddir.joinpath('env').absolute()
    print('ENV DIR: %s' % envdir)
    envbuilder = venv.EnvBuilder(with_pip=True)
    envbuilder.create(envdir)

    print('Creating install and builder scripts...')
    if platform.system() == 'Windows':
        installer_path, builder_path = create_install_batch(envdir, builddir.joinpath('repos').absolute(), wheeldir.absolute(), INSTALL_ORDER)
    else:
        installer_path, builder_path = create_install_linux(envdir, builddir.joinpath('repos').absolute(), wheeldir.absolute(), INSTALL_ORDER)
    
    return installer_path, builder_path

def start(basedir:str = None, ssh_cmd:str = None, ssh_key:str = None, steps:int = 4):
    if basedir is None:
        basedir = pathlib.Path().absolute()
    else:
        basedir = pathlib.Path(basedir).absolute()
    if ssh_cmd is not None and ssh_key is not None:
        print('SSH CMD and SSH KEY cannot be used together!')
        exit(1)
    if ssh_cmd is None:
        if ssh_key is not None:
            git_ssh_identity_file = pathlib.Path(ssh_key).absolute()
        else:
            git_ssh_identity_file = pathlib.Path('~/.ssh/id_rsa').expanduser()
        
        
        if git_ssh_identity_file.exists() is False:
            print('No SSH key found, please specify one! Or use --ssh-cmd to specify a custom command.')
            exit(1)
        if platform.system() == 'Windows':
            # otherwise it doesnt find the file...
            git_ssh_identity_file = str(git_ssh_identity_file).replace('\\', '\\\\')
        ssh_cmd = 'ssh -i %s' % git_ssh_identity_file
    

    print('BASEDIR: %s' % basedir)
    if git_ssh_identity_file is not None:
        print('GIT SSH IDENTITY FILE: %s' % git_ssh_identity_file)
    print('GIT SSH CMD: %s' % ssh_cmd)
    print('Preparing environment and fetching projects...')
    installer_path, builder_path = prepare_env_and_fetch_projects(basedir, ssh_cmd, steps)
    if steps <= 2:
        return
    print('Installer path: %s' % installer_path)
    print('Builder path: %s' % builder_path)
    if installer_path is None:
        print('No installer path, exiting...')
        exit(1)
    print('Running installer...')
    result = os.system(str(installer_path))
    if result != 0:
        print('Installer failed with code %d' % result)
        exit(1)
    if steps <= 3:
        return
    print('Running builder...')
    result = os.system(str(builder_path))
    if result != 0:
        print('Builder failed with code %d' % result)
        exit(1)

    print('Done!')

def main():
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--basedir', help='Base directory for the build', default = None)
    argparser.add_argument('--sshcmd', help='SSH command to use for cloning. MUST contain the SSH key file as well!', default = None)
    argparser.add_argument('--sshkey', help='SSH identity file to use for cloning', default = str(pathlib.Path('~/.ssh/id_rsa').expanduser()))
    argparser.add_argument('--steps', type=int, default = 3, help='1= Fetch repos, 2= Install, 3= Build, 4= All')
    args = argparser.parse_args()
    
    start(args.basedir, args.sshcmd, args.sshkey, args.steps)

if __name__ == '__main__':
    main()
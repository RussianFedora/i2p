# Skip debug package to fix ERROR: No build ID note found in /usr/bin/i2p/i2psvc
%define  debug_package %{nil}

Name:           i2p
Version:        0.9.1
Release:        1%{?dist}
Summary:        Anonymous network I2P

Group:          Applications/Internet
License:        Public domain and BSD and GPL + exeption and Artistic MIT and Apache License 2.0 and Eclipse Public License 1.0 and check the source
URL:            http://www.i2p2.de
Source0:        http://mirror.i2p2.de/i2psource_%{version}.tar.bz2

BuildRequires:  ant
BuildRequires:  expect
BuildRequires:  jetty
BuildRequires:  gettext
Requires:       java
Requires:       jetty
Requires(pre):  /usr/sbin/useradd
Requires(post): chkconfig

%description
I2P is an anonymous network, exposing a simple layer that applications can use
to anonymously and securely send messages to each other. The network itself is
strictly message based (a la IP), but there is a library available to allow
reliable streaming communication on top of it (a la TCP). All communication is
end to end encrypted (in total there are four layers of encryption used when
sending a message), and even the end points ("destinations") are cryptographic
identifiers (essentially a pair of public keys).


%prep
%setup -q


%build
ant pkg

%install
echo "------!!! Install in !!!------"
echo "Folder: $RPM_BUILD_ROOT/opt/%{name}"
# java -jar i2pinstall* -console
expect -c "spawn java -jar i2pinstall.exe -console; expect redisplay; send \"1\r\";
expect path;
send \"$RPM_BUILD_ROOT/opt/%{name}\r\";
expect redisplay;
send \"1\n\";
expect done"

# Remove problematic and unnecessary files
rm $RPM_BUILD_ROOT/opt/%{name}/.installationinformation
rm -rf $RPM_BUILD_ROOT/opt/%{name}/Uninstaller

# Strip buildroot from files
sed -i "s:$RPM_BUILD_ROOT::g" $RPM_BUILD_ROOT/opt/%{name}/eepget
sed -i "s:$RPM_BUILD_ROOT::g" $RPM_BUILD_ROOT/opt/%{name}/runplain.sh
sed -i "s:$RPM_BUILD_ROOT::g" $RPM_BUILD_ROOT/opt/%{name}/wrapper.config
sed -i "s:$RPM_BUILD_ROOT::g" $RPM_BUILD_ROOT/opt/%{name}/i2prouter

# Install i2p service (eq 'i2prouter install')
mkdir -p $RPM_BUILD_ROOT%{_initrddir}
install -m755 $RPM_BUILD_ROOT/opt/%{name}/i2prouter $RPM_BUILD_ROOT%{_initrddir}/i2p

# Remove redundant functionality from i2p service
sed -i "s:^.*gettext.*install.*Install to start automatically.*::g" $RPM_BUILD_ROOT%{_initrddir}/i2p
sed -i "s:^.*gettext.*remove.*Uninstall.*::g" $RPM_BUILD_ROOT%{_initrddir}/i2p
sed -i "s: | install | remove::g" $RPM_BUILD_ROOT%{_initrddir}/i2p

# Use i2p user to run the service
sed -i "s:^#RUN_AS_USER=:RUN_AS_USER=\"i2p\":g" $RPM_BUILD_ROOT%{_initrddir}/i2p

# Fix for upstream bug (runuser and a secure (without a shell) service account)
# Fix: add a shell with -s /bin/sh
sed -i "s:/sbin/runuser -:/sbin/runuser -s /bin/sh -:g" $RPM_BUILD_ROOT%{_initrddir}/i2p

# Append init order to row 2
sed -i '2 a # chkconfig: - 99 10' $RPM_BUILD_ROOT%{_initrddir}/i2p


%posttrans
# Condrestart and return 0
/sbin/service i2p condrestart >/dev/null 2>&1 || :

%post
# Register the i2p service
/sbin/chkconfig --add i2p > /dev/null 2>&1


%pre
# Add the "i2p" user
getent group i2p >/dev/null || groupadd -r i2p
getent passwd i2p >/dev/null || useradd -r -g i2p -s /sbin/nologin -d /usr/local/i2p -c "I2P" i2p
# Create the home diretory for i2p if it not exist (useradd cant do it with selinux enabled)
if [ ! -d "/usr/local/i2p" ]; then
    mkdir /usr/local/i2p
    chown i2p:i2p /usr/local/i2p
fi
exit 0

%preun
# Unregister the i2p service
if [ $1 = 0 ]; then
    /sbin/service i2p stop > /dev/null 2>&1
    /sbin/chkconfig --del i2p > /dev/null 2>&1
fi


%files
%doc
/opt/%{name}
%{_initrddir}/i2p


%changelog
* Wed Aug 22 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 0.9.1-1.R
- Clean spec
- Moved all to /opt

* Tue Jul 10 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.9-3
- Add init order

* Mon Jun 18 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.9-2
- Remove desktop

* Sun May 6 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.9-1
- Update to i2p 0.9

* Tue Apr 10 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.8.13-2
- Change from openjdk 1.7.0 to java.

* Tue Apr 3 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.8.13-1
- Update to 0.8.13

* Wed Mar 28 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.8.12-8
- Add desktop sub package

* Tue Mar 20 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.8.12-7
- Condrestart return 0

* Wed Feb 22 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.8.12-6
- Add service i2p start in post installation

* Mon Feb 20 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.8.12-5
- Add i2p service account

* Sun Feb 19 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.8.12-4
- Use expect for silent install

* Sun Feb 19 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.8.12-3
- Include installation folder in files

* Sun Feb 19 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.8.12-2
- Add i2p init.d service

* Sun Feb 19 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.8.12-1
- Initial package

* Sat Feb 18 2012 Mattias Ohlsson <mattias.ohlsson@inprose.com> - 0.8.12-1
- Initial spec template

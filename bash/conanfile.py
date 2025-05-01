from conan import ConanFile
from conan.tools.files import get, rmdir
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, Autotools
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
import os


class BashConan(ConanFile):
    name = "bash"
    version = "5.2.21"
    license = "GPL-3.0-or-later"
    url = "https://www.gnu.org/software/bash/"
    description = "The GNU Project's Bourne Again SHell"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = {"shared": True}
    exports_sources = "patches/*"

    def build_requirements(self):
        self.tool_requires("bison/3.8.2")
        self.tool_requires("m4/1.4.19")
        self.tool_requires("make/4.3")

    def requirements(self):
        self.requires("ncurses/6.4")

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
        )

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def _dep_lib_paths(self, dep_name):
        dep = self.dependencies[dep_name]
        dep_cpp_info = dep.cpp_info.aggregated_components()
        return [os.path.join(dep.package_folder, dir).replace("\\", "/") for dir in dep_cpp_info.libdirs]

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate(scope="build")

        env = VirtualRunEnv(self)
        env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend(
            [f"--disable-nls", "--enable-rpath"]
        )
        tc.extra_ldflags.append(
            f"-Wl,-rpath,{":".join(self._dep_lib_paths("ncurses"))}"
        )

        env = tc.environment()
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()

        rmdir(self, os.path.join(self.package_folder, "share", "man"))
        rmdir(self, os.path.join(self.package_folder, "share", "doc"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)

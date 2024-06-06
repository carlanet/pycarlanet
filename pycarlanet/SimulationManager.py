from pycarlanet.utils import DecoratorSingleton
import psutil
import signal

@DecoratorSingleton
class SimulationManager:

    def __init__(self, carla_sh_path, options = []) -> None:
        self._carla_simulator_proc = None
        options.insert(0, carla_sh_path)
        self._carla_launch_script = options
        #self._carla_launch_script = [carla_sh_path, '-RenderOffScreen', '>/dev/null', '2>/dev/null']

    def _carla_service_is_active(self):
        return self._carla_simulator_proc is not None and self._carla_simulator_proc.poll() is None

    def _start_process(self):
        self._carla_simulator_proc = psutil.Popen(self._carla_launch_script, stdout=None, stderr=None, shell=False)
        #print(self._carla_simulator_proc.pid)
        while self._carla_simulator_proc.children(recursive=True) == 0:
            ...

    def _stop_process(self):
        def kill_child_processes(parent_pid, sig=signal.SIGTERM):
            try:
                parent = psutil.Process(parent_pid)
            except psutil.NoSuchProcess:
                return
            children = parent.children(recursive=True)
            for process in children:
                # app.logger.warning("====> " + str(process.pid))
                #print("===> Trying to kill chilren process...")
                try:
                    process.kill()
                    process.wait()
                except psutil.NoSuchProcess:  # Catch the error caused by the process no longer existing
                    pass  # Ignore it
        
                
                #print("===> Finished to kill chilren process...")
                
        # app.logger.warning("====> " + str(carla_proc.pid))
        kill_child_processes(self._carla_simulator_proc.pid)
        try:
            self._carla_simulator_proc.kill()
            #print("===> Trying to kill main process...")
            self._carla_simulator_proc.wait()
        except psutil.NoSuchProcess:  # Catch the error caused by the process no longer existing
            pass  # Ignore it
        #print("===> Finished to kill main process...")


    def reload_simulator(self):
        if self._carla_service_is_active():
            #print("===> Trying to stop process...")
            self._stop_process()
            #print("===> Finished to stop process...")

        #print("===> Trying to start process...")
        self._start_process()
        #print("===> Finished to start process...")

        res = {'result': True, 'pid': self._carla_simulator_proc.pid}
        # return json.dumps(res)
        return True

    def close_simulator(self):
        # app.logger.warning("====> " + str(_carla_service_is_active()))
        if self._carla_service_is_active():
            self._stop_process()
        res = {'result': True}
        # return json.dumps(res)
        return True

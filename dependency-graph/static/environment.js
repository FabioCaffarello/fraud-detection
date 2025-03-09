window.exclude = [];
  window.watch = true;
  window.environment = 'release';
  window.localMode = 'build';

  window.appConfig = {
    showDebugger: false,
    showExperimentalFeatures: false,
    workspaces: [
      {
        id: 'local',
        label: 'local',
        projectGraphUrl: 'project-graph.json',
        taskGraphUrl: 'task-graph.json',
        taskInputsUrl: 'task-inputs.json',
        sourceMapsUrl: 'source-maps.json'
      }
    ],
    defaultWorkspaceId: 'local',
  };
  window.projectGraphResponse = {"hash":"de8186dc86b87fa7bf6b11c63c127939d65d28f0b375017315a1a9293b76ca6d","projects":[],"dependencies":{},"fileMap":{},"layout":{"appsDir":"apps","libsDir":"libs"},"affected":[],"focus":null,"groupByFolder":false,"exclude":[],"isPartial":false,"connectedToCloud":true};
    window.taskGraphResponse = {"taskGraphs":{},"errors":{},"plans":{}};
    window.expandedTaskInputsResponse = {};window.sourceMapsResponse = {};
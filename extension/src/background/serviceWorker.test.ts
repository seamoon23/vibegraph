type SidePanelBehavior = {
  openPanelOnActionClick?: boolean;
};

export {};

const panelBehaviorCalls: SidePanelBehavior[] = [];

(globalThis as unknown as { chrome: typeof chrome }).chrome = ({
  action: {
    onClicked: {
      addListener: () => undefined
    }
  },
  runtime: {
    onMessage: {
      addListener: () => undefined
    },
    sendMessage: async <T>() => undefined as T
  },
  tabs: {
    query: async () => [],
    sendMessage: async <T>() => ({ ok: false, reason: 'not used in this test' }) as T
  },
  sidePanel: {
    open: async () => undefined,
    setOptions: async () => undefined,
    setPanelBehavior: async (behavior: SidePanelBehavior) => {
      panelBehaviorCalls.push(behavior);
    }
  },
  scripting: {
    executeScript: async () => []
  },
  storage: {
    local: {
      get: async () => ({}),
      set: async () => undefined
    }
  }
} as unknown) as typeof chrome;

await import('./serviceWorker.js');

if (panelBehaviorCalls.length !== 1) {
  throw new Error(`Expected one setPanelBehavior call, got ${panelBehaviorCalls.length}`);
}

if (panelBehaviorCalls[0]?.openPanelOnActionClick !== true) {
  throw new Error('Expected openPanelOnActionClick to be true');
}

console.log('ok - service worker enables toolbar click side panel behavior');

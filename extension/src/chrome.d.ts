import type { CaptureResponse } from './core/types.js';

type MessageCallback = (response?: CaptureResponse) => void;

declare global {
  namespace ChromeApi {
    interface RuntimeError {
      message?: string;
    }

    interface Runtime {
      lastError?: RuntimeError;
      onMessage: {
        addListener(
          callback: (
            message: unknown,
            sender: MessageSender,
            sendResponse: MessageCallback
          ) => boolean | void
        ): void;
      };
      sendMessage<T = unknown>(message: unknown): Promise<T>;
    }

    interface MessageSender {
      tab?: Tab;
    }

    interface Tab {
      id?: number;
      url?: string;
      title?: string;
      windowId?: number;
    }

    interface Tabs {
      query(queryInfo: {
        active?: boolean;
        currentWindow?: boolean;
      }): Promise<Tab[]>;
      sendMessage<T = unknown>(tabId: number, message: unknown): Promise<T>;
    }

    interface SidePanel {
      open(options: { tabId?: number; windowId?: number }): Promise<void>;
      setPanelBehavior(options: {
        openPanelOnActionClick?: boolean;
      }): Promise<void>;
      setOptions(options: {
        tabId?: number;
        path?: string;
        enabled?: boolean;
      }): Promise<void>;
    }

    interface Action {
      onClicked: {
        addListener(callback: (tab: Tab) => void): void;
      };
    }

    interface Scripting {
      executeScript(options: {
        target: { tabId: number };
        files: string[];
      }): Promise<unknown[]>;
    }

    interface StorageArea {
      get(keys?: string | string[] | Record<string, unknown> | null): Promise<Record<string, unknown>>;
      set(items: Record<string, unknown>): Promise<void>;
    }

    interface Storage {
      local: StorageArea;
    }
  }

  const chrome: {
    action: ChromeApi.Action;
    runtime: ChromeApi.Runtime;
    tabs: ChromeApi.Tabs;
    sidePanel: ChromeApi.SidePanel;
    scripting: ChromeApi.Scripting;
    storage: ChromeApi.Storage;
  };
}

export {};

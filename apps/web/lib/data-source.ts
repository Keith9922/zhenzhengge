export type DataSourceState = "api" | "mock" | "error";

export type ListFetchResult<T> = {
  items: T[];
  source: DataSourceState;
  note?: string;
};

export type DetailFetchResult<T> = {
  item?: T;
  source: DataSourceState;
  note?: string;
};

export function buildDemoDataNote(resource: string) {
  return `当前为演示数据/模拟数据，${resource} 尚未接入真实后端。`;
}

export function getDataSourceLabel(source: DataSourceState) {
  if (source === "api") {
    return "真实数据";
  }

  if (source === "error") {
    return "接口异常";
  }

  return "演示数据";
}


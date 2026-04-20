export type DataSourceState = "api" | "error";

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

export function buildApiErrorNote(resource: string, detail?: string) {
  if (detail) {
    return `${resource} 接口请求失败：${detail}`;
  }

  return `${resource} 接口请求失败，请检查后端服务与环境配置。`;
}

export function getDataSourceLabel(source: DataSourceState) {
  if (source === "api") {
    return "真实数据";
  }

  return "接口异常";
}

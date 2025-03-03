import type { ServerOptions } from "vue3-easy-data-table";

export type NewsPaperSelectorModel = {
  ca?: string;
  provincia?: string;
  engine?: string;
  sub_engine?: string;
};

export type NewsSearch = ServerOptions & {
  notBefore?: Date;
  notAfter?: Date;
}
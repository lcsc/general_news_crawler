import type { ServerOptions } from "vue3-easy-data-table";
import type { BoolEmptyEnum } from "@/newsclient/hey";

export type NewsPaperSelectorModel = {
  ca?: string;
  provincia?: string;
  engine?: string;
  sub_engine?: string;
};

export type NewsSearch = ServerOptions & {
  notBefore?: Date;
  notAfter?: Date;
  category?: Array<string>;
  headline_drought?: BoolEmptyEnum | undefined;
};

export type MapConfigOptions = {
  layer: "Comunidades" | "Provincias" | "Municipios";
};

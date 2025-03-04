import type {
  NewsPaper,
  ClientOptions,
  OptionsResult,
  BcubeCategory,
  NewsArticle,
  NewsSearchResult,
} from "./hey/types.gen";
import type { Client } from "@hey-api/client-axios";
import { createClient, createConfig } from "@hey-api/client-axios";
import {
  options,
  npGet,
  npList,
  npListCcaa,
  npListCcaaProv,
  newsList,
  catList,
} from "./hey/sdk.gen";

import type { NewsPaperSelectorModel, NewsSearch } from "../model/selectors";
import type { Axios, AxiosResponse } from "axios";
import type { ServerOptions } from "vue3-easy-data-table";

export class NewsClient {
  static #instance: NewsClient;
  apiClient: Client;
  serverOptions?: OptionsResult;

  /**
   * The Singleton's constructor should always be private to prevent direct
   * construction calls with the `new` operator.
   */
  private constructor() {
    this.apiClient = createClient(
      createConfig<ClientOptions>({
        baseURL: window.location.origin + "/news/api",
      })
    );
  }

  public static get instance(): NewsClient {
    if (!NewsClient.#instance) {
      NewsClient.#instance = new NewsClient();
    }

    return NewsClient.#instance;
  }

  public async listNewsPapers(
    selector: NewsPaperSelectorModel
  ): Promise<NewsPaper[]> {
    let ret: NewsPaper[] = [];

    if (selector.ca == undefined && selector.provincia == undefined) {
      let response = await npList({
        client: this.apiClient,
        query: {
          engine: selector.engine,
          sub_engine: selector.sub_engine,
        },
      });
      if (response.data) ret = response.data;
    } else if (selector.ca != undefined && selector.provincia == undefined) {
      let response = await npListCcaa({
        client: this.apiClient,
        path: {
          ccaa: selector.ca,
        },
        query: {
          engine: selector.engine,
          sub_engine: selector.sub_engine,
        },
      });
      if (response.data) ret = response.data;
    } else if (selector.ca != undefined && selector.provincia != undefined) {
      let response = await npListCcaaProv({
        client: this.apiClient,
        path: {
          ccaa: selector.ca,
          provincia: selector.provincia,
        },
        query: {
          engine: selector.engine,
          sub_engine: selector.sub_engine,
        },
      });
      if (response.data) ret = response.data;
    } else if (selector.ca == undefined && selector.provincia != undefined) {
      let ca = this.findCa(selector.provincia);
      let response = await npListCcaaProv({
        client: this.apiClient,
        path: {
          ccaa: ca,
          provincia: selector.provincia,
        },
        query: {
          engine: selector.engine,
          sub_engine: selector.sub_engine,
        },
      });
      if (response.data) ret = response.data;
    } else {
      throw new Error("Server error");
    }

    return ret;
  }

  findCa(provincia: string): string {
    if (this.serverOptions && this.serverOptions?.provincias) {
      let provs_data = this.serverOptions.provincias;
      console.log(provs_data);
      for (const [key, value] of Object.entries(provs_data)) {
        //console.log(key);
        for (const p of value) {
          //console.log("   " + p);
          if (p == provincia) return key;
        }
      }
    }

    throw new Error("No CCAA found");
  }

  public async getOptions(): Promise<OptionsResult> {
    if (this.serverOptions) return this.serverOptions;
    let res = await options({
      client: this.apiClient,
    });

    if (res.data) {
      this.serverOptions = res.data;
      return this.serverOptions;
    }
    throw new Error("Server error");
  }

  public async getNewsPaper(
    ccaa: string,
    short_name: string
  ): Promise<NewsPaper> {
    let res = await npGet({
      client: this.apiClient,
      path: {
        ccaa: ccaa,
        short_name: short_name,
        provincia: "*",
      },
    });
    if (res.data) {
      return res.data;
    }

    throw new Error("Server error");
  }

  public async listArticles(
    ccaa: string,
    short_name: string,
    search: NewsSearch
  ): Promise<NewsSearchResult> {
    let res = await newsList({
      client: this.apiClient,
      path: {
        ccaa: ccaa,
        short_name: short_name,
      },
      query: {
        page: search.page,
        rowsPerPage: search.rowsPerPage,
        sortBy: search.sortBy,
        sortType: search.sortType,
        notAfter: search.notAfter?.toISOString().slice(0, 10),
        notBefore: search.notBefore?.toISOString().slice(0, 10),
        category: search.category,
      },
    });
    if (res.data) {
      return res.data;
    }

    throw new Error("Server error");
  }

  public async listCategories(
    ccaa: string,
    short_name: string
  ): Promise<BcubeCategory[]> {
    let res = await catList({
      client: this.apiClient,
      path: {
        ccaa: ccaa,
        short_name: short_name,
      },
    });
    if (res.data) {
      return res.data;
    }

    throw new Error("Server error");
  }
}

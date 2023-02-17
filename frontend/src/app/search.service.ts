import { Injectable } from '@angular/core';
import { HttpClient } from "@angular/common/http";
import { Observable, of } from 'rxjs';
import { map } from "rxjs/operators";


@Injectable({
  providedIn: 'root'
})
export class SearchService {

  public baseUrl = "http://127.0.0.1:5000/query";
  public searchResults: any;

  constructor(private httpClient: HttpClient) { }


  //makes the HTTP request to get the resources and returns the response as observable;  
  public searchEntries(term: string): Observable<any> {
    if (term === "") {
      console.log("Not defined");
      return of(null);
    } else {
      let params = { query: term }
      return this.httpClient.get(this.baseUrl, { params }).pipe(
        map(response => {
          console.log(response)
          return this.searchResults = response;
        })
      );
    }

  }

  //returns the response for the first method
  public _searchEntries(term: string) {
    return this.searchEntries(term);
  }
}

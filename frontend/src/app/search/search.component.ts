import { Observable, of, Subject, throwError } from 'rxjs';
import {
  catchError,
  debounceTime,
  distinctUntilChanged,
  map,
  switchMap,
} from 'rxjs/operators';

import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';

import { QUERY_URL } from '../globals';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css'],
})
export class SearchComponent implements OnInit {
  public loading: boolean = false;
  public searchTerm = new Subject<string>();
  public paginationElements: any;
  public errorMessage: any;
  public page: any;

  public searchResults: any;

  //makes the HTTP request to get the resources and returns the response as observable;
  public searchEntries(term: string): Observable<any> {
    if (term === '') {
      console.log('Not defined');
      return of(null);
    } else {
      let params = { query: term };
      return this.httpClient.get(QUERY_URL, { params }).pipe(
        map((response) => {
          console.log(response);
          return (this.searchResults = response);
        })
      );
    }
  }
  constructor(private httpClient: HttpClient) {}

  public searchForm = new FormGroup({
    search: new FormControl('', Validators.required),
  });

  public search() {
    this.searchTerm
      .pipe(
        debounceTime(400),
        distinctUntilChanged(),
        switchMap((term) => {
          this.loading = true;
          return this.searchEntries(term);
        }),
        catchError((e) => {
          //handle the error and return it
          console.log(e);
          this.loading = false;
          this.errorMessage = e.message;
          return throwError(() => new Error(e));
        })
      )
      .subscribe((v) => {
        this.loading = false;
        // return the results and pass the to the paginate module
        for (let i = 0; i < v.length; ++i) {
          v[i].score = String(v[i].score);
        }
        this.paginationElements = v;
      });
  }

  ngOnInit() {
    this.search();
  }

  similarPages(keywords: [string, number][]) {
    let query = keywords.map((item) => item[0]).join(' ');
    this.searchForm.setValue({ search: query });
    this.searchTerm.next(this.searchForm.getRawValue().search ?? '');
  }
}

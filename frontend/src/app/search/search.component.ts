import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { Subject, throwError } from 'rxjs';
import { map, debounceTime, distinctUntilChanged, switchMap, catchError, retryWhen, retry } from "rxjs/operators";
import { SearchService } from "../search.service";

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent implements OnInit {

  public loading: boolean = false;
  public searchTerm = new Subject<Event>();
  public paginationElements: any;
  public errorMessage: any;
  public page: any;

  constructor(private searchService: SearchService) { }

  public searchForm = new FormGroup({
    search: new FormControl('', Validators.required),
  });

  public search() {
    this.searchTerm.pipe(
      map((e: any) => {
        console.log(e.target.value);
        return e.target.value
      }),
      debounceTime(400),
      distinctUntilChanged(),
      switchMap(term => {
        this.loading = true;
        return this.searchService._searchEntries(term)
      }),
      catchError((e) => {
        //handle the error and return it
        console.log(e)
        this.loading = false;
        this.errorMessage = e.message;
        return throwError(() => new Error(e));
      }),
    ).subscribe(v => {
      this.loading = false;
      //return the results and pass the to the paginate module
      for (let i = 0; i < v.length; ++i) {
        v[i].score = String(v[i].score);
      }
      this.paginationElements = v;
    })
  }


  ngOnInit() {
    this.search();
  }

}
